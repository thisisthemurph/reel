# Reel

Reel scrapes the most up-to-date movies and then scrapes reviews for these.

## Tasks

### TODO

[X] Implement scraping of recent films from Box Office Mojo

[ ] Implement scraping of reviews from Rotten Tomatoes

[ ] Implement scraping of reviews from IMDB

## Tools used

- `Playwright` for scraping websites
- `Selectolax` for parsing HTML
- `FastAPI` for presenting the server rendered user interface
- `Jinja2` for templating
- `Supabase` for the `Postgres` database
 
## Configuration

The following environment variables must be set up:
- `SUPABASE_URL` - the URL for the supabase instance
- `SUPABASE_KEY` - the authentication key for the Supabase instance
