supabot con Gemini

Vamos a hacerlo con docker.

✅ Opción 1: Cargar la variable desde .env y usarla
bash
export $(cat .env | xargs)
docker build -t supabot:$IMAGE_VERSION .
Esto hace dos cosas:

Carga las variables del .env al entorno actual.

Usa $IMAGE_VERSION para etiquetar la imagen.

✅ Opción 2: Usar directamente en el comando (sin exportar)
bash
docker build -t supabot:$(grep IMAGE_VERSION .env | cut -d '=' -f2) .
Esto extrae el valor directamente del .env sin necesidad de exportarlo.





docker build -t supabot:$(grep IMAGE_VERSION ../.env | cut -d '=' -f2) .



# Base de datos

Supabase, logeado con github.
database supabot
uHfx5YDv2Q#H_!.

https://wjyagqbymdpcfdmqlzue.supabase.co


eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndqeWFncWJ5bWRwY2ZkbXFsenVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyNTQ0NzAsImV4cCI6MjA3MzgzMDQ3MH0.fv4cZ9K7Xe4zMOUeU9X35mQaOlaRefwD_YkCJcKAWJQ