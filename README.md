# micro-allinonedd

This project is a microservice that allows for the creation, updating, and deletion of dated markdown files within a GitHub repository, primarily facilitated by a Flask application and GitHub Actions.

## How it Works

This system operates through a combination of a Flask web application and a GitHub Actions workflow:

1.  **Flask Application (`api/index.py`):**
    *   The `/admin/create-post` endpoint handles POST requests containing content for a new markdown file. It encodes this content in Base64.
    *   It then dispatches a `repository_dispatch` event to GitHub with the `event_type` set to `create-dated-file` and the encoded content in the `client_payload`.
    *   The `/admin/update-post` and `/admin/delete-post` endpoints directly interact with the GitHub API to modify or remove existing markdown files in the `contents` directory.

2.  **GitHub Action (`.github/workflows/create-file.yml`):**
    *   This workflow is triggered by the `repository_dispatch` event with the type `create-dated-file`.
    *   Upon activation, it decodes the Base64 content received in the `client_payload`.
    *   It then creates a new markdown file in the `contents` directory, using the current date and time as the filename (e.g., `2025-07-24-10-30-00.md`).
    *   The action commits and pushes the new file to the repository.

## Triggers

The primary trigger for creating new files is a `repository_dispatch` event. This event is programmatically sent to GitHub by the Flask application when a user submits content via the `/admin/create-post` endpoint. The `event_type` for this trigger is `create-dated-file`.

Updates and deletions are triggered by direct GitHub API calls from the Flask application, which modify the repository content.

## Actions

The `create-file.yml` GitHub Action performs the following:

*   **Checkout Code:** Retrieves the repository content.
*   **Create Dated File:** Decodes the Base64 content from the `client_payload` and writes it to a new markdown file named with the current timestamp in the `contents/` directory.
*   **Git Operations:** Configures Git user details, adds the new file, commits it with a descriptive message, and pushes the changes to the `main` branch.

## Token Configuration

This project requires the following environment variables for proper operation, especially for interacting with the GitHub API and triggering actions:

*   `GHTOKEN`: A GitHub Personal Access Token (PAT) is required for the Flask application to dispatch `repository_dispatch` events and to directly interact with the GitHub API for updating and deleting files. This token **must have the `repo` scope** to allow read/write access to your repository.
    *   You can generate a PAT in your GitHub settings under `Developer settings` > `Personal access tokens` > `Tokens (classic)`.
*   `GITHUB_REPOSITORY`: The full name of your GitHub repository (e.g., `IgnatMaldive/micro-allinone2`). This is used by the Flask application to target the correct repository for API calls.

These environment variables should be set in the environment where the Flask application is run.

## Troubleshooting

We recently encountered an issue where the markdown files were being created with the correct filename, but were empty of content. This was due to a combination of issues:

1.  The `api/trigger-action.js` file was not being used. The active endpoint was `/trigger`, which is handled by `api/index.py`.
2.  The `/trigger` endpoint in `api/index.py` was not sending a `client_payload` with content.
3.  The `requests` library was not included in `requirements.txt`, causing a 500 error.
4.  The content was not being correctly passed to the shell environment in the GitHub Action.

The issue was resolved by:

1.  Updating the `/trigger` endpoint in `api/index.py` to send a `client_payload` with Base64 encoded content.
2.  Adding `requests` to `requirements.txt`.
3.  Updating the GitHub Actions workflow to decode the Base64 content before writing it to the file.

## Running Locally

To run the service locally, you can use the following command:

```bash
source myenv/bin/activate && FLASK_APP=api/index.py flask run &
```
