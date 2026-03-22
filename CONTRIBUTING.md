# Contributing to Bottles-Deflatpak

Thanks for taking the time to contribute :heart:!

## Found a Problem?

Before reporting a problem, please make sure that:

1. The [upstream Bottles documentation](https://docs.usebottles.com) does not cover your problem
2. The problem has not already been reported in the [issue tracker](https://github.com/THShafi170/Bottles-Deflatpak/issues)
3. The problem is reproducible with a native (non-Flatpak) build of Bottles-Deflatpak

If all apply, then please [open a new issue](https://github.com/THShafi170/Bottles-Deflatpak/issues/new).

> **Note:** If your issue also affects the upstream Flatpak version of Bottles, please report it to [bottlesdevs/Bottles](https://github.com/bottlesdevs/Bottles/issues) instead.

## Want to Submit Code?

1. [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks) this repository
2. Make your changes (see [Building](README.md#building) and [Coding Guide](CODING_GUIDE.md))
3. Run the pre-commit checks: `./venv/bin/python -m pre_commit run --all-files`
4. Submit a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)

## GitHub Actions & Nix (Cachix)

If you have forked this repository and want to automate your Nix builds with binary caching, you can set up Cachix in your own CI/CD pipeline:

1.  **Create a Cache**: Sign up at [cachix.org](https://cachix.org) and create a new public or private cache.
2.  **Auth Token**: Generate an **Auth Token** in your cache settings.
3.  **GH Secrets**: Add the following secrets to your GitHub repository (**Settings > Secrets and variables > Actions**):
    -   `CACHIX_CACHE_NAME`: The name of your Cachix cache (e.g., `my-bottles-cache`).
    -   `CACHIX_AUTH_TOKEN`: Your generated authentication token.

The GitHub Actions workflow (`package.yml`) is configured to detect these secrets. If they are present, it will automatically push all newly built Nix store paths to your cache during the build process, ensuring that subsequent builds and tests are significantly faster.

## Want to Translate Bottles?

Translations are managed upstream. You can help via [Weblate](https://hosted.weblate.org/projects/bottles).
