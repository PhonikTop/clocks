#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}Applying database migrations...${NC}"
python manage.py migrate

echo -e "${YELLOW}Creating superuser...${NC}"
python manage.py createsuperuser --noinput

if [ "$1" ]; then
    exec "$@"
else
    echo -e "${BLUE}Starting uvicorn server...${NC}"
    uvicorn settings.asgi:application --reload --host 0.0.0.0 --port 8000
fi
