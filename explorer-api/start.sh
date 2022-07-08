#! /usr/bin/env sh

if [ -z $ENVIRONMENT ] || [ "$ENVIRONMENT" = "dev" ]; then
    ENVIRONMENT="dev"
fi

echo "==========================="
echo "Environment: $ENVIRONMENT"
echo "==========================="

# Set path
# export PYTHONPATH=$PYTHONPATH:$PWD/py-substrate-interface/:$PWD/py-scale-codec/

echo "Running gunicorn..."

if [ "$ENVIRONMENT" = "dev" ]; then
    gunicorn -b 0.0.0.0:8000 --workers=1 app.main:app --reload --timeout 600
fi

if [ "$ENVIRONMENT" = "prod" ]; then
    gunicorn -b 0.0.0.0:8000 --workers=5 app.main:app --worker-class="egg:meinheld#gunicorn_worker"
fi
