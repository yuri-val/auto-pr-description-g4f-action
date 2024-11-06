import os
import json
from github import Github
from subprocess import check_output
from github import GithubException
from g4f.client import Client


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

        if not github_token:
            raise ValueError('GitHub token not provided as input.')

        context = get_github_context()
        print("GitHub context: {context}")

        if context.get('event_name') != 'pull_request':
            raise ValueError('This action only runs on pull_request events.')

        pr_number = context['pull_request']['number']
        base_ref = context['pull_request']['base']['ref']
        head_ref = context['pull_request']['head']['ref']

        # Set up Git
        os.system('git config --global user.name "github-actions[bot]"')
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')

        # Fetch branches
        os.system(f'git fetch origin {base_ref} {head_ref}')

        # Get the diff
        diff_output = check_output(f'git diff origin/{base_ref} origin/{head_ref}', shell=True, encoding='utf-8')

        # Generate the PR description
        generated_description = generate_description(diff_output, temperature)
        retry_count = 0
        max_retries = 10
        generated_description = None

        while retry_count < max_retries:
            generated_description = generate_description(diff_output, temperature)
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
        print(f'Action failed: {e}')


def generate_description(diff_output, temperature):
    prompt = f"""**Instructions:**

Please generate a **Pull Request description** for the provided diff, following these guidelines:
- Add appropriate emojis to the description.
- Do **not** include the words "Title" and "Description" in your output.
- Format your answer in **Markdown**.

**Diff:**
{diff_output}"""

    client = Client()
    chat_completion = client.chat.completions.create(
        model="gpt-4",
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
        max_tokens=1024,
    )

    description = chat_completion.choices[0].message.content.strip()
    return description


def update_pr_description(github_token, context, pr_number, generated_description):
    g = Github(github_token)
    repo = g.get_repo(f"{context['repository']['owner']['login']}/{context['repository']['name']}")
    pull_request = repo.get_pull(pr_number)

    current_description = pull_request.body or ''
    new_description = f'---\n{generated_description}'

    try:
        if current_description and not current_description.startswith('---\n'):
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
    print("Environment Variables:")
    for key, value in os.environ.items():
        print(f"{key}: {value}")
    main()
