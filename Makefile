api:
	uvicorn projects.api.api:api

tailwind:
	tailwindcss -i projects/api/tailwind/app.css -o projects/api/static/css/app.css --config projects/api/tailwind.config.js --watch