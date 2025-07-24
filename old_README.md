# micro-allinone2

This project is a microservice that uses a GitHub Action to create dated markdown files. The service is triggered by a POST request to the `/trigger` endpoint.

## How it Works

1.  A POST request is sent to `/trigger`.
2.  The `api/index.py` script receives the request and triggers a `repository_dispatch` event on GitHub.
3.  The `.github/workflows/create-file.yml` GitHub Action is triggered by the `repository_dispatch` event.
4.  The action creates a new markdown file in the `contents` directory with the current date and time as the filename.

## Configuration

The following environment variables are used to configure the application:

*   `GHTOKEN`: A GitHub personal access token with the `repo` scope.
*   `GITHUB_REPOSITORY`: The name of the GitHub repository (e.g., `IgnatMaldive/micro-allinone2`).

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
