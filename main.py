import os
import json
import g4f
from github import Github, GithubException
from subprocess import check_output, CalledProcessError
from g4f.client import Client
from g4f.Provider import BaseProvider


def get_github_context():
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if not event_path:
        raise EnvironmentError('GITHUB_EVENT_PATH not found in environment variables.')
    with open(event_path, 'r') as f:
        return json.load(f)


def main():
    try:
        # Inputs
        github_token = os.getenv('INPUT_GITHUB_TOKEN')
        temperature = float(os.getenv('INPUT_TEMPERATURE', '0.7'))
        provider_name = os.environ.get('INPUT_PROVIDER', 'g4f.Provider.Bing')
        model_name = os.environ.get('INPUT_MODEL', 'gpt-4')

        event_name = os.getenv('GITHUB_EVENT_NAME')

        print(f"Temperature: {temperature}")
        print(f"Event name: {event_name}")
        if not github_token:
            raise ValueError('GitHub token not provided as input.')

        context = get_github_context()
        
        if event_name != 'pull_request':
            raise ValueError('This action only runs on pull_request events.')

        pr_number = context['pull_request']['number']
        base_ref = context['pull_request']['base']['ref']
        head_ref = context['pull_request']['head']['ref']

        print(f"PR number: {pr_number}")
        print(f"Base ref: {base_ref}")
        print(f"Head ref: {head_ref}")
        
        # Set up Git
        os.system('git config --global --add safe.directory /github/workspace')
        os.system('git config --global user.name "github-actions[bot]"')
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')

        # Fetch branches
        print(f"Fetching branches: {base_ref} and {head_ref}")
        fetch_result = os.system(f'git fetch origin {base_ref} {head_ref}')
        if fetch_result != 0:
            raise RuntimeError(f"Failed to fetch branches. Exit code: {fetch_result}")

        # Get the diff
        print(f"Getting diff between origin/{base_ref} and origin/{head_ref}")
        try:
            diff_output = check_output(f'git diff origin/{base_ref} origin/{head_ref}', shell=True, encoding='utf-8', stderr=-1)
        except CalledProcessError as e:
            print(f"Error output: {e.stderr}")
            raise RuntimeError(f"Failed to get diff. Exit code: {e.returncode}")

        print("Diff obtained successfully")
        print(f"Diff length: {len(diff_output)} characters")

        # Generate the PR description
        retry_count = 0
        max_retries = 10
        generated_description = None

        while retry_count < max_retries:
            generated_description = generate_description(diff_output, temperature, provider_name, model_name)
            print(f"Generated description (attempt {retry_count + 1}):")
            print(generated_description[:100] + "..." if len(generated_description) > 100 else generated_description)
            if generated_description != "No message received":
                break
            retry_count += 1
            print(f"Retry {retry_count}/{max_retries}: No message received. Retrying...")

        if generated_description == "No message received":
            raise Exception("Failed to generate description after maximum retries")

        # Update the PR
        update_pr_description(github_token, context, pr_number, generated_description)

        print(f'Successfully updated PR #{pr_number} description.')

    except Exception as e:
        print(f'Action failed: {str(e)}')
        raise

def get_provider_class(provider_name):
    if provider_name == 'auto':
        return None
    try:
        provider_class = getattr(g4f.Provider, provider_name.split('.')[-1])
        if not issubclass(provider_class, BaseProvider):
            raise ValueError(f"Invalid provider: {provider_name}")
        return provider_class
    except AttributeError:
        raise ValueError(f"Provider not found: {provider_name}")
    
def generate_description(diff_output, temperature, provider_name, model_name):
    
    provider_class = get_provider_class(provider_name)

    prompt = f"""**Instructions:**

Please generate a **Pull Request description** for the provided diff, following these guidelines:
- Add appropriate emojis to the description.
- Do **not** include the words "Title" and "Description" in your output.
- Format your answer in **Markdown**.

**Diff:**
{diff_output}"""

    client = Client(provider=provider_class)
    print(f"Sending request to GPT-4 with temperature {temperature}")
    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                'role': 'system',
                'content': 'You are a helpful assistant who generates pull request descriptions based on diffs.',
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ],
        temperature=temperature,
        max_tokens=2048,
    )

    description = chat_completion.choices[0].message.content.strip()
    print(f"Received response from {model_name}. Length: {len(description)} characters")
    return description


def update_pr_description(github_token, context, pr_number, generated_description):
    g = Github(github_token)
    repo = g.get_repo(f"{context['repository']['owner']['login']}/{context['repository']['name']}")
    pull_request = repo.get_pull(pr_number)

    current_description = pull_request.body or ''
    new_description = f"""> `AUTO DESCRIPTION`
> by [auto-pr-description-g4f-action](https://github.com/yuri-val/auto-pr-description-g4f-action)
\n{generated_description}
"""

    try:
        if current_description and not current_description.startswith('> `AUTO DESCRIPTION`'):
            print('Creating comment with original description...')
            pull_request.create_issue_comment(f'**Original description**:\n\n{current_description}')
            print('Comment created successfully.')

        print('Updating PR description...')
        pull_request.edit(body=new_description)
        print('PR description updated successfully.')

    except GithubException as e:
        print(f'Error updating PR description: {e}')
        raise


if __name__ == '__main__':
    main()
