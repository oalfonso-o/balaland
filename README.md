# BALALAND

This is a 2D shooter game to test PyGame lib. The goal is to create the same experience as a 1st person shooter with the same vision range and mechanic effect but being a 2D shooter, this means that the crosshair is going to be fixed and the camera is the one that is going to rotate and you can't see behind the walls.

The camera rotation is something that you won't see in many games because the effect it produces is not very pleasent, is a bit dizzy, but it's interesting to test it.

The shadowcasting to prevent the user seeing behind walls is not implemented yet, is work in progress.

The enemies only follow you for now, it's pending to implement that they can shoot or do melee attacks.

[gameplay.webm](https://github.com/oalfonso-o/balaland/assets/9935204/ce4884e4-0e29-4549-bde2-6d92e8333bf3)



Prerequisites for installation:

- python >=3.8

Installation instructions:

1. Copy environment variables file
```
cp .env.example .env
```
2. Customize params (if you know what you are editing, if not you can leave it as default)
3. Install game (with python >= 3.8)
```
pip install -e .
```
4. Run game
```
balaland
```

