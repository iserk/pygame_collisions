# Pygame Collisions Experiment

## 🛫 Introduction
This is a simple experiment to test collisions in pygame.  
The game is a minimalistic 2D airplane simulator where the player can move the airplane up and down with the arrow keys.  
Mountains are randomly generated and the player must avoid them.  

## 🎮 Controls
`↑` or `w` — Move the airplane up    
`↓` or `s` — Move the airplane down   
`←` or `a` — Decelerate the airplane  
`→` or `d` — Accelerate the airplane

`Esc` — Quit the game  
`Space` — Restart the game (when the game is over)  

## 🏁 Objective
To win the game, the player must avoid the mountains and land the airplane on the ground.

## 📦 Requirements
`Python` 3.x +  
`Pygame` 2.x +  

## 🔧 Cloning the Repository
```
git clone git@github.com:iserk/pygame_collisions.git
cd pygame_collisions 
```

## 🚀 Running
```
pip install -r requirements.txt
python main.py
```

## 📝 Collision Detection Algorith
This program uses a simple collision detection algorithm that checks if two polygons are overlapping.  
The algorithm is based on the [Separating Axis Theorem](https://en.wikipedia.org/wiki/Hyperplane_separation_theorem).
