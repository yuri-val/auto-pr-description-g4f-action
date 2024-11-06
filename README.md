# Auto-generate PR Description Action

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

This GitHub Action automatically generates pull request descriptions using GPT-4 via the gpt4free library when a PR is created or updated.

## 🚀 Features

- Automatically generates detailed PR descriptions based on the diff between branches
- Uses GPT-4 for intelligent and context-aware descriptions
- Customizable temperature setting for generation
- Preserves original PR description as a comment
- Handles retries in case of generation failures

## 📋 Usage

To use this action in your workflow, add the following step to your `.github/workflows/main.yml` file:

```yaml
name: Auto-generate PR Description
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  generate-pr-description:
    runs-on: ubuntu-latest
    steps:
      - name: Generate PR Description
        uses: yuri-val/auto-pr-description-g4f-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          temperature: 0.7
```

## 📊 Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github_token` | GitHub token with repo permissions | Yes | `${{ github.token }}` |
| `temperature` | Sampling temperature for gpt4free (0.0 to 1.0) | No | 0.7 |

## 📈 Outputs

| Output | Description |
|--------|-------------|
| `pr_number` | The number of the pull request updated |
| `description` | The generated pull request description |

## 🛠️ Development

To set up this project locally:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/auto-pr-description-g4f-action.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make your changes to the `main.py` file.

4. Test your changes locally before creating a pull request.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/yourusername/auto-pr-description-g4f-action/issues) if you want to contribute.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgements

- [gpt4free](https://github.com/xtekky/gpt4free) for providing free access to GPT-4
- [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API integration

