
set -e

# Default DB host and port
DB_HOST=${DB_HOST:-mysql}
DB_PORT=${DB_PORT:-3306}

echo "🔄 Waiting for MySQL at $DB_HOST:$DB_PORT..."
tries=0
until nc -z "$DB_HOST" "$DB_PORT" || [ $tries -ge 30 ]; do
  tries=$((tries+1))
  printf '.'
  sleep 1
done
echo "\n✅ MySQL is up!"

# Initialize the DB if INIT_DB=1 and init_academiq.sql exists
if [ "$INIT_DB" = "1" ] && [ -f /app/init_academiq.sql ]; then
  echo "📘 Initializing database..."
  for i in 1 2 3 4 5; do
    mysql -h "$DB_HOST" -u"$DB_ROOT_USER" -p"$DB_ROOT_PASSWORD" "$DB_NAME" < /app/init_academiq.sql && break || sleep 2
  done
  echo "✅ Database initialized."
fi

echo "🚀 Starting Flask app..."
exec python server.py
