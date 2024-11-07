# Auto-generate PR Description Action [G4F]

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

This GitHub Action automatically generates pull request descriptions using GPT-4 via the gpt4free library when a PR is created or updated.

## 🚀 Features

- Automatically generates detailed PR descriptions based on the diff between branches
- Uses GPT-4 or other models for intelligent and context-aware descriptions
- Customizable temperature setting for generation
- Supports different G4F providers
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
        uses:hqnicolas/auto-pr-description-g4f-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          temperature: 0.7
          provider: auto
          model: gpt-4
```

## 📊 Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github_token` | GitHub token with repo permissions | Yes | `${{ github.token }}` |
| `temperature` | Sampling temperature for gpt4free (0.0 to 1.0) | No | 0.7 |
| `provider` | G4F provider to use [docs](docs/providers-and-models.md) | No | auto |
| `model` | Model to use with the selected provider [docs](docs/providers-and-models.md) | No | gpt-4 |

## 📈 Outputs

| Output | Description |
|--------|-------------|
| `pr_number` | The number of the pull request updated |
| `description` | The generated pull request description |

## 🛠️ Development

To set up this project locally:

1. Clone the repository:
   ```
   git clone https://github.com/yuri-val/auto-pr-description-g4f-action.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make your changes to the `main.py` file.

4. Test your changes locally before creating a pull request.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/yuri-val/auto-pr-description-g4f-action/issues) if you want to contribute.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgements

- [gpt4free](https://github.com/xtekky/gpt4free) for providing free access to GPT-4 and other models
- [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API integration

## 🧑‍💻 Author

Yuri V
