import numpy as np
import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 60

class Cell:
    # TODO: Write Cell class docstring 
    def __init__(self, i: int, j: int, size: float, alive: bool = False) -> None:
        """Initialise une cellule à une position donnée sur la grille.

        Args:
            i (int): la position verticale de la cellule sur la grille.
            j (int): la position horizontale de la cellule sur la grille.
            size (float): la taille de la cellule.
            alive (bool, optional): l'état initial de la cellule. Par défaut False.
        """
        self.i = i
        self.j = j
        self.rect = pygame.Rect(i * size, j * size, size, size)
        self.alive = alive

    def toggle(self) -> None:
        """Inverse l'état de vie de la cellule."""
        self.alive = not self.alive

    def draw(self, surface: pygame.Surface) -> None:
        """Dessine la cellule sur une surface donnée.

        Args:
            surface (pygame.Surface): la surface sur laquelle dessiner la cellule.
        """
        pygame.draw.rect(surface, BLACK, self.rect)


class Grid:
    # TODO: #1 Write Grid class docstring 
    def __init__(self, n_rows: int, n_cols: int, cell_size: float) -> None:
        """Initialise une grille de cellules.

        Args:
            n_rows (int): le nombre de rangées de la grille.
            n_cols (int): le nombre de colonnes de la grille.
            cell_size (float): la taille de chaque cellule.
        """
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.cell_size = cell_size
        self.cells = np.array(
            [
                [Cell(i, j, self.cell_size) for j in range(self.n_cols)]
                for i in range(self.n_rows)
            ]
        )

    def neighbors(self, cell: "Cell") -> list["Cell"]:
        """Retourne une liste des cellules voisines de la cellule donnée.

        Args:
            cell (Cell): la cellule dont on veut connaître les voisines.

        Returns:
            list[Cell]: la liste des cellules voisines de la cellule donnée.
        """
        return [
            self.cells[i][j]
            for i in range(max(cell.i - 1, 0), min(cell.i + 2, self.n_rows))
            for j in range(max(cell.j - 1, 0), min(cell.j + 2, self.n_cols))
            if not (i == cell.i and j == cell.j)
        ]

    def count_alive_neighbors(self, cell: "Cell") -> int:
        """Compte le nombre de voisines vivantes de la cellule donnée.

        Args:
            cell (Cell): la cellule dont on veut connaître le nombre de voisines vivantes.

        Returns:
            int: le nombre de voisines vivantes de la cellule donnée.
        """
        return sum(neighbor.alive for neighbor in self.neighbors(cell))

    def rule(self, cell: "Cell") -> bool:
        """Applique la règle du jeu de la vie pour une cellule donnée.

        Si la cellule est vivante et a moins de 2 ou plus de 3 voisines vivantes,\
        elle meurt de solitude ou de surpopulation. 
        Si la cellule est morte et entourée d'exactement trois voisins elle revit.

        Args:
            cell (Cell): la cellule en question.

        Returns:
            bool: l'état de la cellule doit être changé?

        """

        return (cell.alive and not 2 <= self.count_alive_neighbors(cell) <= 3) or (
            not cell.alive and self.count_alive_neighbors(cell) == 3
        )

    def update(self) -> None:
        """Applique la règle du jeu de la vie à toute les cellules de la grille."""
        cells_to_toggle = list(filter(self.rule, self.cells.flatten()))
        for cell in cells_to_toggle:
            cell.toggle()

    def draw(self, surface: pygame.Surface) -> None:
        """Dessine la grille et ses cellules

        Args:
            surface (pygame.Surface): la surface sur laquelle dessiner la cellule.
        """
        for i in range(self.n_rows + 1):
            pygame.draw.line(
                surface,
                BLACK,
                (0, i * self.cell_size),
                (self.n_cols * self.cell_size, i * self.cell_size),
            )

        for j in range(self.n_cols + 1):
            pygame.draw.line(
                surface,
                BLACK,
                (j * self.cell_size, 0),
                (j * self.cell_size, self.n_rows * self.cell_size),
            )

        for cell in self.cells.flatten():
            if not cell.alive:
                continue

            cell.draw(surface)

    def toggle(self, i: int, j: int) -> None:
        """Toggle a cell at a given position in the grid

        Args:
            i (int): row index
            j (int): column index
        """
        cell = self.cells[i][j]
        cell.toggle()


class Game:
    # TODO: Write Game class docstring 
    def __init__(self, n_rows: int, n_cols: int, cell_size: float):
        pygame.init()
        pygame.font.init()

        self.cell_size = cell_size
        self.height = n_rows * self.cell_size
        self.width = n_cols * self.cell_size

        # création de la fenêtre de jeu
        self.window_size = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Le jeu de la vie")

        # création de la grille de cellules
        self.grid = Grid(n_rows, n_cols, self.cell_size)

        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = True
        self.commands = [
            "Commands",
            "Press RETURN: PAUSE/UNPAUSE the game",
            "Left click: toggle a cell",
        ]

    def display_commands(self, commands=None) -> None:
        """Display the list of commands on the screen.

        Args:
            commands (list[str], optional): List of commands to display. Defaults to None.
        """
        if commands is None:
            commands = self.commands

        # Set up the font
        font_size = 20
        font = pygame.font.SysFont(name="cominsans", size=20)

        # Loop through the commands and display each one
        pos_y = 10
        for command in commands:
            text_surface = font.render(command, True, BLACK)
            self.screen.blit(text_surface, (10, pos_y))
            pos_y += font_size + 5

    def handle_events(self) -> None:
        """Draw the game on the screen."""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                    break
                case pygame.KEYDOWN if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                self.grid.toggle(pos[0] // self.cell_size, pos[1] // self.cell_size)

    def draw(self) -> None:
        """dessiner la grille de cellules"""
        self.screen.fill(WHITE)  # effacer l'écran
        self.display_commands()
        self.grid.draw(self.screen)

    def run(self) -> None:
        """Run the game loop until the user quits the game."""
        while self.running:
            self.handle_events()

            if not self.paused:
                self.grid.update()

            self.draw()

            pygame.display.flip()

            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game(100, 100, 10)
    game.run()
