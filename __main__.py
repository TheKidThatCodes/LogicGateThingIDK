import sys
import pygame
import random

pygame.init()

ssm = 1.5
ssmf = lambda x: x * ssm
fps = 60
_debug = True


def debug(msg: str) -> None:
    if _debug:
        print(f"[DEBUG] {msg}")


size = width, height = ssmf(1000), ssmf(500)

screen = pygame.display.set_mode(size)


class Chip:
    def __init__(
        self,
        enabledpins: dict[
            str,
            dict[
                (int, bool),
                str,
            ],
        ],
        chipname: str,
        _id: str,
        colour: tuple[int, int, int] = None,
    ) -> None:
        self.colour = colour or (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        self.enabledpins = enabledpins
        self.name = chipname
        self.id = _id

    def tick(self, pins: dict[str, dict[int, bool]]) -> dict[str, dict[int, bool]]:
        """defines the behaviour of the chip per tick

        Returns:
            dict[str,dict[int,bool]]: the pins to be set
        """
        pass


class IOChip(Chip):
    def __init__(
        self,
    ) -> None:
        self.colour = (100, 100, 100)
        # self.enabledpins = enabledpins
        self.name = "IO"
        self.state: bool = False

    def tick(self) -> None:
        ...


wirelist = dict[
    tuple[
        tuple[
            int,
            int,
            str,
            int,
        ],
        tuple[
            int,
            int,
            str,
            int,
        ],
    ],
    bool,
]
chipgridlist = dict[tuple[int, int], Chip]


def chipgrid_tick(chipgrid: chipgridlist, wires: wirelist) -> wirelist:
    for loc, chip in chipgrid.items():
        if isinstance(chip, IOChip):
            dict[
                str,
                dict[
                    (int, bool),
                    str,
                ],
            ]
            for wire in wires:
                if wire[0][0] == loc and wire[0][1] == "ep":
                    wires[wire] = True if chip.state or wires[wire] else False
                elif wire[1][0] == loc and wire[1][1] == "ep":
                    wires[wire] = True if chip.state or wires[wire] else False
    for loc, chip in {
        k: v for k, v in chipgrid.items() if not isinstance(v, IOChip)
    }.items():
        chipinput = {
            l: {x: False for x in range(1, 9)}
            for l in [
                "n",
                "s",
                "e",
                "w",
            ]
        }
        for wire, ison in wires.items():
            {((1, 1, "n", 1), (1, 1, "n", 2)): True}
            if wire[0][0:1] == loc:
                chipinput[wire[0][2]][wire[0][3]] = ison
            elif wire[1][0:1] == loc:
                chipinput[wire[1][2]][wire[1][3]] = ison
        if not chip.name == "ep":
            chipoutput = chip.tick(chipinput)

            for side, pins in chipoutput.items():
                for pin, ison in pins.items():
                    for wire in wires:
                        if wire[0] == (loc, side, pin):
                            wires[wire] = True if ison or wires[wire] else False
                        elif wire[1] == (loc, side, pin):
                            wires[wire] = True if ison or wires[wire] else False
    return wires


class CustomChip(Chip):
    def __init__(
        self,
        enabledpins: dict[str, dict[int, str]],
        chipname: str,
        _id: str,
        colour: tuple[int, int, int] = None,
    ):
        super().__init__(enabledpins, chipname, _id, colour)

    def tick(self, pins: dict[str, dict[int, bool]]) -> dict[str, dict[int, bool]]:
        chipgrid_tick(pins)


class PreDefChip_And(Chip):
    def __init__(self):
        super().__init__({"w": {3: "i", 6: "i"}, "e": {4: "o"}}, "And", "and")

    def tick(self, pins: dict[str, dict[int, bool]]) -> dict[str, dict[int, bool]]:
        return {"e": {4: True}} if pins["w"][3] and pins["w"][6] else {"e": {4: False}}


class PreDefChip_Not(Chip):
    def __init__(self):
        super().__init__(
            {
                "w": {
                    4: "i",
                },
                "e": {
                    4: "o",
                },
            },
            "Not",
            "not",
        )

    def tick(self, pins: dict[str, dict[int, bool]]) -> dict[str, dict[int, bool]]:
        return {"e": {4: not pins["w"][3]}}


class PreDefChip_Or(Chip):
    def __init__(self):
        super().__init__({"w": {3: "i", 6: "i"}, "e": {4: "o"}}, "Or", "or")

    def tick(self, pins: dict[str, dict[int, bool]]) -> dict[str, dict[int, bool]]:
        return {"e":{4:any(v for k, v in pins["w"].items())}}


chipgrid: chipgridlist = {}
wires: wirelist = {}


def renderchip(gridspace: tuple[int, int], chip: Chip):
    x, y = gridspace
    pygame.draw.rect(
        screen, chip.colour, ((x * 50 * ssm, y * 50 * ssm), (50 * ssm, 50 * ssm))
    )
    if isinstance(chip, IOChip):
        pygame.draw.ellipse(
            screen,
            (0, 0, 0),
            (
                (
                    x * 50 * ssm + 18.75 * ssm,
                    y * 50 * ssm + 18.75 * ssm,
                ),
                (12.5 * ssm, 12.5 * ssm),
            ),
        )
    elif not isinstance(chip, IOChip):
        for side, pins in chip.enabledpins.items():
            if side == "n":
                for psn, ispin in pins.items():
                    if ispin:
                        pygame.draw.ellipse(
                            screen,
                            (0, 0, 0),
                            (
                                (
                                    x * 50 * ssm
                                    + 8 * ssm
                                    + ((psn * 4.5 * ssm) - 6.25 * ssm),
                                    (y * 50 * ssm),
                                ),
                                (4.5 * ssm, 4.5 * ssm),
                            ),
                        )
            if side == "s":
                for psn, ispin in pins.items():
                    if ispin:
                        pygame.draw.ellipse(
                            screen,
                            (0, 0, 0),
                            (
                                (
                                    x * 50 * ssm
                                    + 8 * ssm
                                    + ((psn * 4.5 * ssm) - 6.25 * ssm),
                                    (y * 50 * ssm + 46 * ssm),
                                ),
                                (4.5 * ssm, 4.5 * ssm),
                            ),
                        )
            if side == "e":
                for psn, ispin in pins.items():
                    if ispin:
                        pygame.draw.ellipse(
                            screen,
                            (0, 0, 0),
                            (
                                (
                                    x * 50 * ssm + 46 * ssm,
                                    (
                                        y * 50 * ssm
                                        + 8 * ssm
                                        + ((psn * 4.5 * ssm) - 6.25 * ssm)
                                    ),
                                ),
                                (4.5 * ssm, 4.5 * ssm),
                            ),
                        )
            if side == "w":
                for psn, ispin in pins.items():
                    if ispin:
                        pygame.draw.ellipse(
                            screen,
                            (0, 0, 0),
                            (
                                (
                                    x * 50 * ssm,
                                    (
                                        y * 50 * ssm
                                        + 8 * ssm
                                        + ((psn * 4.5 * ssm) - 6.25 * ssm)
                                    ),
                                ),
                                (4.5 * ssm, 4.5 * ssm),
                            ),
                        )


def is_xy_chip_pin(x, y) -> tuple[int, int, int, int] | None:
    # if an xy is on a chip pin, return the chip xz on the board, the side, and the pin number
    for chiploc in chipgrid:
        all([
            x >= (chiploc[0] * 50 * ssm + 8 * ssm + ((1 * 4.5 * ssm) - 6.25 * ssm)),
            y >= (chiploc[1] * 50 * ssm),
            x
            <= (
                (chiploc[0] * 50 * ssm + 8 * ssm + ((1 * 4.5 * ssm) - 6.25 * ssm))
                + 4.5 * ssm
            ),
            y <= ((chiploc[1] * 50 * ssm) + 4.5 * ssm),
        ])

        chiploc[0] * 50 * ssm, chiploc[1] * 50 * ssm


# for x in range(1, 9):
#     for y in range(1, 9):
# screen.fill(
#     (
#         random.randint(0,255),
#         random.randint(0,255),
#         random.randint(0,255),
#         ),
#     (
#         (
#             x*50,
#             y*50,
#             ),
#         (
#             # (i*10)+10,
#             # (i*10)+10,
#             50,
#             50,
#             )
#         )
#     )
templine = {
    "s": None,
    "e": None,
}
chipgrid[
    (
        1,
        1,
    )
] = PreDefChip_And()
#     {s: {x: "io" for x in range(1, 9, )} for s in "nsew"},
#     "test",
#     "test",
# )
chipgrid[
    (
        1,
        0,
    )
] = IOChip()
istempline = False
drawthing = True
lines: list[dict[str, dict[int, bool]]] = []
chipgrid_tick(chipgrid=chipgrid, wires=wires)
while True:
    screen.fill(
        (
            0,
            0,
            0,
        ),
    )
    screen.fill((127.5, 127.5, 127.5), ((0, 0), (500 * ssm, 500 * ssm)))
    # lines = []
    if drawthing:
        drawthing = False
    for loc, chip in chipgrid.items():
        renderchip(loc, chip)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            debug(f"{event.pos}, {event.button}")
            debug(f"ischippin {is_xy_chip_pin(event.pos[0], event.pos[1])}")
            if event.button == 1:
                if istempline:
                    debug("e")
                    templine["e"] = event.pos
                    lines.append(templine)
                    istempline = False
                    templine = {
                        "s": None,
                        "e": None,
                    }
                else:
                    debug("else")
                    templine["s"] = event.pos
                    istempline = True
                debug(templine)
            elif event.button == 3:
                lines = []
    # if istempline: screen.blit(pygame.draw.line(screen,(0,0,0),templine["s"],templine["e"],1))
    if lines:
        [
            pygame.draw.line(screen, (0, 0, 0), l["s"], l["e"], int(1.5 * ssm))
            for l in lines
        ]
    pygame.display.flip()
    # make it run at the selected fps
    pygame.time.delay(round(1000 / fps))
