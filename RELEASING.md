# Publishing and versioning Velide

The current release is **v1.0.0**. Source publication and Windows release uploads are manual.

## First publication

1. On GitHub, create a repository owned by **Baloide**, named **velide**. Choose the visibility you want. Leave the initial README, `.gitignore` and license options unchecked: this project already contains its own files. A source license has not yet been selected.
2. Open PowerShell in the project folder and run:

```powershell
Set-Location 'C:\Users\lamag\IdeaProjects\Baloide\clinical-redactor'
git init -b main
git add .
git status
git commit -m "Release Velide v1.0.0"
git remote add origin https://github.com/Baloide/velide.git
git tag -a v1.0.0 -m "Velide v1.0.0"
git push -u origin main
git push origin v1.0.0
```

If Git requests your identity, set `git config user.name "Your name"` and `git config user.email "Your GitHub email"` for this repository, then retry the commit. Complete GitHub's sign-in prompt when pushing. Do not use force-push to solve a rejected upload; check whether the remote already contains commits.

`git status` lets you inspect what will be committed before creating the commit. Build outputs, dependencies, local `.env` files and generated screenshots are excluded by `.gitignore`. Keep actual sensitive documents outside the source tree.

## Publish the downloadable Windows release

In the repository, open **Releases → Draft a new release**:

- Select the existing tag **v1.0.0**.
- Use the title **Velide v1.0.0**.
- Use the v1.0.0 entry in [CHANGELOG.md](CHANGELOG.md) as the release notes.
- Attach the four files below from the local `dist` folder.
- Publish as a normal release, rather than a pre-release, and mark it latest if needed.

| Asset | Purpose |
| :--- | :--- |
| `Velide-Setup.exe` | Recommended Windows x64 installer. |
| `Velide-Windows.zip` | Complete portable Windows x64 app. |
| `Velide-Setup.exe.sha256` | Installer checksum. |
| `Velide-Windows.zip.sha256` | Portable ZIP checksum. |

Keep these asset names unchanged: the README download buttons use GitHub's latest-release URLs. GitHub's automatically generated source ZIP does not contain the bundled Windows application. Do not commit the installer or ZIP into source history.

After publication, open the README download links and confirm that they resolve to this release. The build generates packages locally; it does not create a GitHub repository, push code or publish releases.

## Future releases

Version numbers follow `MAJOR.MINOR.PATCH`: for example, `1.0.1` for fixes, `1.1.0` for compatible new features, and `2.0.0` for incompatible changes. Git tags add a `v` prefix; API and Electron metadata omit it.

1. Update the version using the synchronization script:

```powershell
backend/.venv/Scripts/python.exe scripts/set_version.py 1.0.1
```

This updates the API version module, Electron package and lockfile, footer fallback and README. The footer also reads the running service version. Add the new release notes to `CHANGELOG.md`.

2. Run the tests and rebuild the Windows packages:

```powershell
backend/.venv/Scripts/python.exe scripts/set_version.py --check
backend/.venv/Scripts/python.exe -m unittest discover -s tests -v
backend/.venv/Scripts/python.exe scripts/build_windows.py
```

3. Commit the tested source and tag that exact commit:

```powershell
git add .
git commit -m "Release Velide v1.0.1"
git tag -a v1.0.1 -m "Velide v1.0.1"
git push origin main
git push origin v1.0.1
```

4. Create the corresponding GitHub release and upload its freshly built assets. Do not move an already published tag or replace its files with a different version; publish a new version instead.

References: [GitHub source publication](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github), [GitHub release management](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
