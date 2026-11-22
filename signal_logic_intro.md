## Naming conventions

Object ids follow the pattern `<station><type><number>`, for example `is03` = Sigdal, signal 03. The station and type letters below come from `DMJK-Adresser.pdf` and the plan. Where the meaning is not written down anywhere, the table says "probably".

### Station letter (first letter)

| Letter | Station            |
|--------|--------------------|
| s      | Solberg            |
| g      | Solberg Skiftegård |
| k      | Kobbarvik          |
| m      | Mjøndalen          |
| y      | Myra               |
| i      | Sigdal             |
| n      | Norbotten          |
| h      | Havna              |

### Type letter (second letter)

| Pattern     | Rocrail object | Meaning                                                                        | Examples                    |
|-------------|----------------|--------------------------------------------------------------------------------|-----------------------------|
| `?s##`      | `sg` signal    | Signal                                                                         | is03, ys05, ms13            |
| `?v##`      | `sw` switch    | Turnout (veksel), Lenz LS100 decoder                                           | iv01, yv06                  |
| `?x##`      | `sw` switch    | Crossing (`sx`) or double slip (`yx01`, kryssveksel)                           | sx, yx01                    |
| `?d##`      | `fb` sensor    | Sensor on an RS-8/RS-16-O module. Either a track detector or a panel input, see below | yd05, id16            |
| `?b##`      | `co` output    | Route button (bryter), test setup                                              | ib11-ib22                   |
| `?o...`     | `co` output    | Virtual output used as a flag in the interlocking logic (no address)           | ioINy, koCtl, yoP1          |
| `?rt-<a><b>`| `st` route     | Route (togvei) from station or block a to b                                    | krt-is, nrt-i2-n7           |
| `?tx...`    | `tx` text      | Text on the panel                                                              | stxDir                      |
| `<letter><n>` | `bk` block   | Rocrail block                                                                  | i2, k1, n-i1                |

### Words inside output names (`?o...`)

| Part            | Meaning                                                              | Example                                |
|-----------------|----------------------------------------------------------------------|----------------------------------------|
| `IN<x>`         | Entry (innkjør) from station x                                       | `ioINy` = Sigdal, entry from Myra      |
| `UT<x>`         | Exit (utkjør) towards station x                                      | `ioUTy` = Sigdal, exit towards Myra    |
| `RT<x>p`        | Route request from station x is pending                              | `koRTip` = Kobbarvik, request from Sigdal |
| `RT<x>d`        | Route direction ("mot ...")                                          | `koRTid` = Kobbarvik, from Sigdal towards g |
| `Ctl`           | Control: active while a request is handled                           | `koCtl`, `ys01ctl`                     |
| `Occ`           | Occupied (belegg)                                                    | `koOcc`                                |
| `Tmr`, `T`      | Timer                                                                | `koOccTmr`, `koOccT`                   |
| `P1`, `P2`      | Level crossing (planovergang)                                        | `yoP1`, `moP1`                         |
| `Ski`, `Sloc`   | Local shunting (lokal skifting)                                      | `moSki`, `soSloc`                      |
| `LF`, `LFlok`   | Probably lock to local control ("Lås k til lokal styring")           | `koLF`, `koLFlok`                      |
| suffix `d`      | Probably a held copy of a sensor's occupancy                         | `yd03d`, `gd06d`                       |

### Signal aspects in DMJK-Adresser.pdf

Each aspect line in the PDF is `<signal> <type><aspect>`, for example `is03 IY`.

| Type letter | Signal type                         | Aspect letter | Meaning                                       |
|-------------|-------------------------------------|---------------|-----------------------------------------------|
| H           | Main signal (hovedsignal)           | R             | Red / red blink / orange blink, by type       |
| U           | Exit main signal (utkjør)           | G             | Green / 2 green / green blink, by type        |
| B           | Block signal                        | Y             | 1 green / orange-green blink, by type         |
| I           | Entry main signal (innkjør)         | W             | White, dwarf signal only                      |
| F           | Distant signal (forsignal)          | ----          | Dark (no aspect)                              |
| D           | Dwarf signal (dvergsignal)          |               |                                               |
| L           | Light on/off                        |               |                                               |

## Turnouts vs. panel switches

In Rocrail and in English, "switch" means two different things here:

1. **Turnout** (veksel): the track switch. Rocrail object `sw`, id `?v##`, for example `iv01`. In this document, "switch" in section 1 always means a turnout.
2. **Panel switch** (bryter on the control panel): an operator input such as "utkjør mot y". It is wired to an RS-16-O input, so in Rocrail it is a sensor (`fb`), and its id uses the same `?d##` pattern as the track detectors.

The id doesn't tell a panel switch apart from a track detector. Use the `desc` field or the comment in the PDF instead. These sensors are panel switches:

| Station    | Panel switches                                                                 |
|------------|--------------------------------------------------------------------------------|
| Solberg    | sd05 (ut i/r), sd06 (inn i/r), sd07 (inn g/k), sd08 (ut g/i/m/h), sd18/sd19 (exit selector bit 0/1), sd21 (ut H0m) |
| Skiftegård | gd08 (ut s), gd09 (ut i/m/h), gd10 (mot i), gd11 (mot h)                       |
| Mjøndalen  | md09 (ut g/s), md10 (inn k), md11 (inn y), md12 (ut y), md13 (skift), md14 (mot g) |
| Havna      | hd02 (mot g), hd03 (ut g/s)                                                    |
| Sigdal     | id16 (ut y), id17 (inn y), id18 (inn s), id19 (ut s), id20 (mot g), id21 (mot n) |

In this document, "turnout" means the track switch and "panel switch" means the operator input. If the ids are ever changed, a separate type letter for panel switches (for example `?p##`) would remove the ambiguity. That would mean renaming objects in Rocrail and in every action condition, so it isn't done here.
