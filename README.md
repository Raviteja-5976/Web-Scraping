# Web API for DuckDuckGo Search Summarizer

This is a FastAPI-based web service that performs DuckDuckGo searches, scrapes and summarizes the top results, and exposes them via a REST API.

## How to Deploy on Render

1. **Copy the `webapi` folder to a new GitHub repository.**
2. **Push the repository to GitHub.**
3. **Create a new Web Service on [Render](https://render.com/):**
   - Select your repository.
   - Set the build and start commands to default (Render will use `requirements.txt` and `render.yaml`).
   - The service will be available at `https://<your-app-name>.onrender.com/search?query=...`

## Local Development

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the server:
   ```sh
   uvicorn main:app --reload
   ```

## API Usage

- **GET /search?query=your+search+terms**
  - Returns a list of search results with summaries.

## Files
- `main.py`: FastAPI app code
- `requirements.txt`: Python dependencies
- `render.yaml`: Render deployment config
