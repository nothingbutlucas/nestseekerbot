# NestSeekerBot

## Introducción

La idea de este bot es que te tire cada x tiempo los nuevos departamentos o casas que estes buscando.

Para hacer esto estoy usando como base un bot de telegram que me encontre hace 3 años en una publicación que no pude volver a encontrar, asique los creditos van para alguna persona en internet que hizo un posteo.

Este bot basicamente va a determinadas urls, extrae los anuncios, se fija si ya los miro antes y en caso de que no, te lo envía por telegram y luego marca como que la vio.

Lo que hice fue volver a revivir este bot, haciendole un minimo refactor porque tenía muchos oneliners y el codigo no tenía ningún comentario.

Además adapte las variables como los tokens y el chatid para que sean variables de entorno. También buildee la imagen en docker para que se pueda levantar facilmente desde por ejemplo un synology NAS o una raspberry sin mucha vuelta. (El bot consume entre 40 y 80 mb de ram, asíque corre en cualquier lado)

También actualice la captura de las url a día de hoy para que funcione con mercadolibre, zonaprop y argenprop (cada pagina maneja las publicaciones como se les canta, entonces hay que hacer un mapeo para cada pagina).

## Funcionamiento del bot

Esta es una explicación a alto nivel como para entender lo que viene después que es la "instalación", en la parte de instalación explico los detalles de como hacer cada cosa.

Basicamente hay que crear un bot de telegram desde telegram. Esto se hace yendo al bots de todos los bots, [@botfather](https://t.me/BotFather).
Ese bot te va a dar un token. Con ese token podes pegarle a la api de telegram para mandar las publicaciones nuevas a un grupo de telegram o a tu chat personal con el bot.

Luego necesitas el identificador de un grupo de telegram (roomid) o el id de tu usuario. Para obtenerlo vamos a levantar un bot provisorio solo para obtener este dato, luego lo damos de baja.

Lista la parte de telegram.

Con respecto al server no hay mucha vuelta, lo vas a necesitar para correr la imagen de docker con el bot. Tiene que estar conectada a internet para poder scrapear los distintos sitios. Podes ejecutarlo en una raspberry pi, un nas synology o incluso desde algún dispositivo android usando [tmux](https://github.com/tmux/tmux).

## Prerequisitos

Para que este bot funcione vas a necesitar:

* Tener conocimientos de [Docker](https://docs.docker.com/get-started/)
* Tener una cuenta en [Telegram](https://telegram.org/) para crear el bot y ver los mensajes que manda
* Servidor / Computadora / Algo con un procesador y ram, conectada a internet con docker instalado para ejecutar el bot
* Saber tu id o el id del grupo para que el bot pueda enviarte mensajes

Voy a explicar solo el último punto ya que para los 2 primeros hay links y para el 3ero no es necesario entender algo más allá de la oración.

### Saber tu id o el id del grupo

El id de telegram es un numero que te asigna telegram a tu cuenta o que asigna a cada grupo o super-grupo que se crea.
Para saber tu id o el id del grupo, podes usar un bot que desarrolle especificamente para eso: [telegram-id-sender-bot](https://github.com/nothingbutlucas/telegram-id-sender-bot)
Lo piola es que también usa docker y vas a tener que configurar un docker-compose por lo que si no tenes muy claro lo de docker te sirve de practica para luego levantar el bot de las propiedades.

## Instalación

### Configuración en Telegram

#### Crear el bot con botfather

Basicamente vas a telegram a hablar con el [@botfather](https://t.me/botfather) para crear un bot y obtener un token.

Link a la fuente: [https://core.telegram.org/bots#how-do-i-create-a-bot](https://core.telegram.org/bots#how-do-i-create-a-bot)

### Configuración desde el servidor

### Clonar este repositorio

```bash
git clone https://github.com/nothingbutlucas/nestseekerbot.git
cd nestseekerbot
```

#### Buildear la imagen (Opcional)

Este paso es opcional porque la imagen ya la *buildee* y subi a [dockerhub](https://hub.docker.com/r/nothingbutlucas/nestseekerbot)

~~~ bash
docker build -t nestseekerbot:1.0 .
~~~

#### Crear el docker-compose

Podes usar como base el que esta en este repositorio:

```yaml
version: "3.9"
services:
  app:
    image: nothingbutlucas/nestseekerbot:1.0 # Este es el nombre de la imagen, si la buildeaste vos, ponele el nombre que le pusiste si no, dejalo así
    environment:
      TOKEN: "TEKKEN" # Este es el token que te dio botfather
      ROOM: "-4815162342" # Este es el id de tu grupo
      LOGGING_LEVEL: INFO # Este es el nivel de log que va a tener el bot, yo recomiendo los primeros días dejarlo en INFO y luego de 1 o 2 semanas de que funcione bien se puede subir a ERROR
      HORAS: 3 # Esto determina cada cuanto tiempo el bot va a ir a buscar las nuevas propiedades. 3 horas a mi me funciona bien, podes ponerle menos o más, anda fijandote de que los sitios no te bloqueen. En caso de que te bloqueen lo vas a ver en los logs como error.
    command: ["python3", "-u", "main.py"] # Ejecución del bot
    volumes: # Estos volumenes los hago para poder modificar las frases o sitios sin tener que entrar al contenedor. Y el seen.txt te sirve para que si lo apagas, lo vuelvas a prender y no te lleguen propiedades que ya te llegaron.
      - /home/user/ruta/donde/tengas/el/repo/seen.txt:/app/seen.txt
      - /home/user/ruta/donde/tengas/el/repo/frases.txt:/app/frases.txt
      - /home/user/ruta/donde/tengas/el/repo/sitios.txt:/app/sitios.
    # - SERVIDOR                                       :CONTENEDOR DE DOCKER
```

#### Crear archivos de configuración (sitios.txt y frases.txt)

Podes usar como base los archivos del repo.
Tene en cuenta que buscar casa es una mierda porque las fotos estan sacadas como el culo, las casas suelen ser inhabitables y esta todo carisimo.
No podes hacer nada para cambiar esto, pero lo que si podes hacer es armarte las url para que te traiga lo que necesites y unas frases que te saquen una sonrisa cada vez que te llegue una casa de mierda.
Las url las metes en sitios.txt, una url por linea y las frases las metes en frases.txt, una frase por linea.
Basicamente el bot va iterando por cada linea y va haciendo los requests.

## Ejecución

``` bash
docker-compose up -d
```

### Logs

Si ves que no te esta mandando nada hace un tiempo y sospechas que algo anda mal, anda a ver los logs

Para ver los logs, haces lo mismo que con cualquier contenedor de docker:

``` bash
docker logs -f nestseekerbot
```

Y ahí ves que onda. Puede ser que la busqueda que hayas hecho sea demasiado especifica y que por eso no te este trayendo nada, porque no hay nada que traer.

### Cosas a tener en cuenta a la hora de usar este bot

Te recomiendo no poner muchos filtros en las publicaciones, yo pondría un precio maximo, el tipo de propiedad y la zona.
No mucho más porque si empezas con los filtros de m2 o que tenga x cantidad de habitaciones o cosas así es muy probable que te pierdas muchas publicaciones ya que muy poca gente publica correctamente las propiedades.

## Errores y problemas conocidos

El único error que me encontre es ponerle un tiempo muy bajo en la variable de HORAS y que los sitios me bloqueen los requests ó que al cabo de un tiempo me empiecen a devolver codigos 400, supongo que por alguna movida de firewall. Por ahora lo que me funciono fue meterle un random a los sleeps para que sean siempre distintos, pero no se tampoco cuanto tiempo funcionara. La vez que me bloquearon, reinicie el server y volvio a funcionar. También aumente el tiempo de la variable HORAS.

## Mejoras

Una mejora podría ser integrar este bot con [ptb](https://github.com/python-telegram-bot/python-telegram-bot) y poder configurar todo directamente desde el bot.
Incluso así podrías montar el bot y que lo pueda usar más gente, directamente desde telegram.
