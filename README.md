# NestSeekerBot

## Introducción

La idea de este bot es que te tire cada X tiempo los nuevos departamentos o casas que estés buscando.

Para hacer esto estoy usando como base un bot de telegram que me encontré hace 3 años en una publicación que no pude volver a encontrar, asique los créditos van para alguna persona en internet que hizo un posteo. (?

Este bot básicamente va a determinadas urls, extrae los anuncios, se fija si ya los miró antes y en caso de que no, te lo envía por telegram y luego marca como que la vió.
Lo que hice fue volver a revivir este bot, haciendole un mínimo refactor porque tenía muchos oneliners y el código no tenía ningún comentario.

Además adapte las variables como los tokens y el chatid para que sean variables de entorno. También buildee y subí la imagen a [dockerhub](https://hub.docker.com/r/nothingbutlucas/nestseekerbot) para que se pueda levantar facilmente desde, por ejemplo, un synology NAS o una raspberry sin mucha vuelta. (El bot consume entre 40 y 80 mb de ram, asíque corre en cualquier lado).

También actualicé la captura de las url a día de hoy para que funcione con mercadolibre, zonaprop y argenprop (cada página maneja las publicaciones como se les canta, entonces hay que hacer un mapeo para cada página).

## Funcionamiento del bot

Esta es una explicación a alto nivel como para entender lo que viene después que es la "instalación". En esa parte explico los detalles de como hacer cada cosa.

Básicamente, hay que crear un bot de telegram desde telegram.

Luego necesitas el identificador de un grupo de telegram (roomid) o el id de tu usuario.

Lista la parte de telegram.

Con respecto al server, tiene que estar conectado a internet para poder scrapear los distintos sitios. Podes ejecutarlo en una raspberry pi, un nas synology o incluso desde algún dispositivo android usando [tmux](https://github.com/tmux/tmux).

En este server vas a necesitar la imagen de docker, un archivo de sitios.txt para poner las urls de los sitios y un archivo frases.txt para poner un texto previo a la url.

## Prerequisitos

Para que este bot funcione vas a necesitar:

* Tener conocimientos de [Docker](https://docs.docker.com/get-started/)
* Tener una cuenta en [Telegram](https://telegram.org/) para crear el bot y ver los mensajes que manda
* Servidor / Computadora / Algo con un procesador y ram, conectada a internet, con docker instalado para ejecutar el bot
* Saber tu id o el id del grupo para que el bot pueda enviarte mensajes

Voy a explicar sólo el último punto ya que para los 2 primeros hay links y para el 3ero no es necesario entender algo más allá de la oración.

### Saber tu id o el id del grupo

El id de telegram es un número que te asigna telegram a tu cuenta o que asigna a cada grupo o super-grupo que se crea.
Para saber tu id o el id del grupo, podes usar un bot que desarrollé específicamente para eso: [telegram-id-sender-bot](https://github.com/nothingbutlucas/telegram-id-sender-bot)
Lo piola es que también usa docker y vas a tener que configurar un docker-compose, por lo que si no tenes muy claro lo de docker, te sirve de práctica para luego levantar el bot de las propiedades.

## Instalación

### Configuración en Telegram

#### Crear el bot con botfather

Sencillamente, vas a telegram a hablar con el [@botfather](https://t.me/botfather) para crear un bot y obtener un token.

Link a la fuente donde la gente de telegram explica como hacer esto: [https://core.telegram.org/bots#how-do-i-create-a-bot](https://core.telegram.org/bots#how-do-i-create-a-bot)

### Configuración desde el servidor

### Clonar este repositorio

```bash
git clone https://github.com/nothingbutlucas/nestseekerbot.git
cd nestseekerbot
```

#### Buildear la imagen (Opcional)

Este paso es opcional porque la imagen ya la *buildee* (Y se buildea con cada release) y subí a [dockerhub](https://hub.docker.com/r/nothingbutlucas/nestseekerbot)

~~~ bash
docker build -t nestseekerbot:latest .
~~~

#### Crear el docker-compose

Podes usar como base el que está en este repositorio:

```yaml
services:
  app:
    image: nothingbutlucas/nestseekerbot:latest # Este es el nombre de la imagen, si la buildeaste vos, ponele el nombre que le pusiste si no, dejalo así
    environment:
      TOKEN: "TEKKEN" # Este es el token que te dió botfather
      ROOM: "-4815162342" # Este es el id de tu grupo o chatid
      LOGGING_LEVEL: INFO # Este es el nivel de log que va a tener el bot, yo recomiendo los primeros días dejarlo en INFO y luego de 1 o 2 semanas de que funcione bien se puede subir a ERROR
      HORAS: 3 # Esto determina cada cuanto tiempo el bot va a ir a buscar las nuevas propiedades. 3 horas a mi me funciona bien, podes ponerle menos o más, anda fijandote que los sitios no te bloqueen. En caso de que te bloqueen lo vas a ver en los logs como ERROR.
    command: ["python3", "-u", "main.py"] # Ejecución del bot
    volumes: # Estos volumenes los hago para poder modificar las frases o sitios sin tener que entrar al contenedor. Y el seen.txt te sirve para que si lo apagas, lo vuelvas a prender y no te lleguen propiedades que ya te llegaron.
      - /home/user/ruta/donde/tengas/el/repo/seen.txt:/app/seen.txt
      - /home/user/ruta/donde/tengas/el/repo/frases.txt:/app/frases.txt
      - /home/user/ruta/donde/tengas/el/repo/sitios.txt:/app/sitios.txt
      - /home/user/ruta/donde/tengas/el/repo/denylist.txt:/app/denylist.txt
    # - SERVIDOR                                       :CONTENEDOR DE DOCKER
```

#### Crear archivos de configuración (sitios.txt, frases.txt y seen.txt)

Podes usar como base los archivos de este repo.

En el archivo sitios.txt tenes que poner las url de las páginas web junto con los filtros que quieras.
Para hacer esto vas a la página web, le pones los filtros que necesites, te copias la url y la pones en el archivo sitios.txt.
Como tip: podes irte a la página 2 y copiar también esa url.
Vas a ver que te va a agregar un parametro de número de página.
Ahí lo que podes hacer es poner 5 páginas para atrás por cada sitio como para tener los últimos sitios y no perderte ninguno.
Es importante agregar también el orden por **más recientes**. Así te van a aparecer de los más nuevos a los más viejos y si aparece uno nuevo, el bot te lo va a mandar

En el archivo frases.txt pones frases previas a la url.
Tene en cuenta que buscar casa es una mierda porque las fotos estan sacadas como el culo, las casas suelen ser inhabitables y esta todo carísimo.
No podes hacer nada para cambiar esto, pero lo que sí podes hacer, es armarte las url para que te traiga lo que necesites y unas frases que te saquen una sonrisa cada vez que te llegue una casa de mierda.

Las url las metes en sitios.txt, una url por línea y las frases las metes en frases.txt, una frase por línea.

El archivo denylist.txt puede estar vacio. Este archivo lo que hace es filtrar una url. El caso de uso es:

Suponiendo que una url dice: https://sitio.deptos/departamento-monoambiente-24-metros

Si en el archivo denylist tenes las palabras: departamento o monoambiente o 24 o metros, la url se va a filtrar y no se va a enviar a telegram

El bot va iterando por cada línea y se trae los anuncios de esa página. Se fija en el archivo seen.txt si ya te lo mandó.
Si lo tiene, sigue con el siguiente anuncio.
Si no lo tiene, te lo manda y luego lo graba en el archivo seen.txt.

## Ejecución

``` bash
docker-compose up -d
```

### Logs

Si ves que no te está mandando nada hace un tiempo y sospechas de que algo anda mal, anda a ver los logs.

Para ver los logs, haces lo mismo que con cualquier contenedor de docker:

``` bash
docker logs -f nestseekerbot
```

Y ahí ves qué onda. Puede ser que la busqueda que hayas hecho sea demasiado específica y que por eso no te este trayendo nada, porque no hay nada que traer.

### Cosas a tener en cuenta a la hora de usar este bot

Te recomiendo no poner muchos filtros en las publicaciones, yo pondría un precio máximo, el tipo de propiedad y la zona.

No mucho más, porque si empezas con los filtros de m2 o que tenga x cantidad de habitaciones o cosas así, es muy probable que te pierdas muchas publicaciones, ya que muy poca gente publica correctamente las propiedades.

## Errores y problemas conocidos

### Repetición

* Si ves que te manda las mismas casas repetidas, puede ser porque reiniciaste el bot y no le pasaste bien el volumen donde tenes el seen.txt en el docker-compose o porque la misma propiedad se publicó en distintos sitios web.

### El bot no envía ninguna publicación de ningún sitio

Un error que me encontré, es ponerle un tiempo muy bajo en la variable de HORAS y que los sitios me bloqueen los requests ó que al cabo de un tiempo me empiecen a devolver códigos 400, supongo que por alguna movida de firewall.

Por ahora, lo que me funcionó fue meterle un random a los sleeps para que sean siempre distintos, pero no sé tampoco cuanto tiempo funcionara. La vez que me bloquearon, reinicié el server y volvió a funcionar. También aumenté el tiempo de la variable HORAS a 3. Fijate si tiene sentido porque si miras el celu 1 vez por día, de última ponelo que mire cada 12 hs o algo así.

### El bot no envía ninguna publicación de zonaprop

Bueno, zona prop es un tema aparte. Si miras el código, vas a ver que los divs en donde esta el post tiene un id rarisimo.
Bueno, la onda es que ese id va cambiando con el tiempo. No se cuanto tiempo. Tampoco se porque cambia.
Supongo que debe ser para justamente evitar bots, pero no lo se, tampoco lo investigue.
Puede que haya una forma dinamica de obtener este id, pero no encontre una por el momento.
La solución sería ir a la web, F12 y chusmear el id del div dentro de `div.postings-container` que contenga la url y eso:

## Mejoras

Una mejora podría ser integrar este bot con [ptb](https://github.com/python-telegram-bot/python-telegram-bot) y poder configurar todo directamente desde el bot.

Incluso así podrías montar el bot y que lo pueda usar más gente desde telegram.

