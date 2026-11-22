# Signal logic in 20261119232535091-DMJK-Layout.xml

Grouped by station, from the first letter of the signal or target id.
Conditions: `type:id=state`. `and` = all required, `(a or b)` = at least one.

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


## Solberg (s)

### 1. Turnouts that affect signals

| Signal | Aspect | Turnout | How | Full condition |
|---|---|---|---|---|
| ss01 | green | sv01 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=straight and sw:sv03=straight and fb:sd09=false and fb:sd13=false |
| ss01 | green | sv02 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=straight and sw:sv03=straight and fb:sd09=false and fb:sd13=false |
| ss01 | green | sv03 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=straight and sw:sv03=straight and fb:sd09=false and fb:sd13=false |
| ss01 | red | sv01 | condition straight (required), trigger sg:ss16=green | sw:sv04=straight and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv01 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv01 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv01 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and sw:sv03=straight and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv01 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and sw:sv03=turnout and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv02 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and sw:sv03=straight and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv02 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and sw:sv03=turnout and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv02 | condition turnout (required), trigger sg:ss16=green | sw:sv04=straight and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv02 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv02 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv03 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and sw:sv03=straight and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv03 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and sw:sv03=turnout and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv04 | condition straight (required), trigger sg:ss16=green | sw:sv04=straight and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv04 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv04 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv05 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv05 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv06 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv07 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv08 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv08 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv09 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv09 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv10 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and sw:sv03=straight and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv10 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and sw:sv03=turnout and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv11 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv11 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv11 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and sw:sv03=straight and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv11 | condition turnout (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and sw:sv03=turnout and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv13 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv13 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv13 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and sw:sv03=straight and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv13 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and sw:sv03=turnout and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv15 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv15 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | sv15 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and sw:sv03=straight and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | sv15 | condition straight (required), trigger sg:ss16=yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and sw:sv03=turnout and sw:sv02=straight and sw:sv01=straight |
| ss01 | yellow | sv01 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=straight and sw:sv03=turnout and fb:sd09=false and fb:sd14=false |
| ss01 | yellow | sv01 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=straight and fb:sd09=false and fb:sd12=false |
| ss01 | yellow | sv01 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=straight and fb:sd09=false and fb:sd11=false |
| ss01 | yellow | sv01 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=straight and fb:sd09=false and fb:sd10=false |
| ss01 | yellow | sv01 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=turnout and fb:sd09=false and fb:sd17=false |
| ss01 | yellow | sv02 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=straight and sw:sv03=turnout and fb:sd09=false and fb:sd14=false |
| ss01 | yellow | sv02 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=straight and fb:sd09=false and fb:sd12=false |
| ss01 | yellow | sv02 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=straight and fb:sd09=false and fb:sd11=false |
| ss01 | yellow | sv02 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=straight and fb:sd09=false and fb:sd10=false |
| ss01 | yellow | sv02 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=turnout and fb:sd09=false and fb:sd17=false |
| ss01 | yellow | sv03 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=straight and sw:sv03=turnout and fb:sd09=false and fb:sd14=false |
| ss01 | yellow | sv04 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=straight and fb:sd09=false and fb:sd12=false |
| ss01 | yellow | sv04 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=straight and fb:sd09=false and fb:sd11=false |
| ss01 | yellow | sv04 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=straight and fb:sd09=false and fb:sd10=false |
| ss01 | yellow | sv04 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=turnout and fb:sd09=false and fb:sd17=false |
| ss01 | yellow | sv05 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=straight and fb:sd09=false and fb:sd11=false |
| ss01 | yellow | sv05 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=straight and fb:sd09=false and fb:sd10=false |
| ss01 | yellow | sv05 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=turnout and fb:sd09=false and fb:sd17=false |
| ss01 | yellow | sv06 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=straight and fb:sd09=false and fb:sd10=false |
| ss01 | yellow | sv06 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=turnout and fb:sd09=false and fb:sd17=false |
| ss01 | yellow | sv07 | condition straight (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=straight and fb:sd09=false and fb:sd10=false |
| ss01 | yellow | sv07 | condition turnout (required), trigger co:soINi=on | sw:sv01=straight and sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=turnout and fb:sd09=false and fb:sd17=false |
| ss05 | green | sv02 | condition straight (required), trigger co:soUTi=on | sw:sv03=turnout and sw:sv02=straight and fb:sd09=false |
| ss05 | green | sv03 | condition turnout (required), trigger co:soUTi=on | sw:sv03=turnout and sw:sv02=straight and fb:sd09=false |
| ss06 | green | sv01 | condition straight (required), trigger co:soUTi=on | sw:sv03=straight and sw:sv02=straight and sw:sv01=straight and fb:sd09=false |
| ss06 | green | sv01 | condition turnout (required), trigger co:soUTi=on | sw:sv03=straight and sw:sv02=straight and sw:sv01=turnout and fb:sd09=false |
| ss06 | green | sv02 | condition straight (required), trigger co:soUTi=on | sw:sv03=straight and sw:sv02=straight and sw:sv01=straight and fb:sd09=false |
| ss06 | green | sv02 | condition straight (required), trigger co:soUTi=on | sw:sv03=straight and sw:sv02=straight and sw:sv01=turnout and fb:sd09=false |
| ss06 | green | sv03 | condition straight (required), trigger co:soUTi=on | sw:sv03=straight and sw:sv02=straight and sw:sv01=straight and fb:sd09=false |
| ss06 | green | sv03 | condition straight (required), trigger co:soUTi=on | sw:sv03=straight and sw:sv02=straight and sw:sv01=turnout and fb:sd09=false |
| ss07 | green | sv02 | condition turnout (required), trigger co:soUTi=on | sw:sv04=straight and sw:sv02=turnout and fb:sd09=false |
| ss07 | green | sv04 | condition straight (required), trigger co:soUTi=on | sw:sv04=straight and sw:sv02=turnout and fb:sd09=false |
| ss08 | green | sv02 | condition turnout (required), trigger co:soUTi=on | sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss08 | green | sv04 | condition turnout (required), trigger co:soUTi=on | sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss08 | green | sv05 | condition straight (required), trigger co:soUTi=on | sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss09 | green | sv02 | condition turnout (required), trigger co:soUTi=on | sw:sv07=straight and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss09 | green | sv04 | condition turnout (required), trigger co:soUTi=on | sw:sv07=straight and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss09 | green | sv05 | condition turnout (required), trigger co:soUTi=on | sw:sv07=straight and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss09 | green | sv06 | condition straight (required), trigger co:soUTi=on | sw:sv07=straight and sw:sv06=straight |
| ss09 | green | sv07 | condition straight (required), trigger co:soUTi=on | sw:sv07=straight and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss09 | green | sv07 | condition straight (required), trigger co:soUTi=on | sw:sv07=straight and sw:sv06=straight |
| ss10 | green | sv02 | condition turnout (required), trigger co:soUTi=on | sw:sv07=turnout and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss10 | green | sv04 | condition turnout (required), trigger co:soUTi=on | sw:sv07=turnout and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss10 | green | sv05 | condition turnout (required), trigger co:soUTi=on | sw:sv07=turnout and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss10 | green | sv06 | condition straight (required), trigger co:soUTi=on | sw:sv07=turnout and sw:sv06=straight |
| ss10 | green | sv06 | condition turnout (required), trigger co:soUTi=on | sw:sv07=turnout and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss10 | green | sv07 | condition turnout (required), trigger co:soUTi=on | sw:sv07=turnout and sw:sv06=straight |
| ss10 | green | sv07 | condition turnout (required), trigger co:soUTi=on | sw:sv07=turnout and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and fb:sd09=false |
| ss11 | green | gv01 | condition straight (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss11 | green | sv08 | condition turnout (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss11 | green | sv08 | condition turnout (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss11 | green | sv09 | condition turnout (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss11 | green | sv09 | condition turnout (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss11 | green | sv11 | condition straight (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss11 | green | sv11 | condition straight (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss11 | green | sv13 | condition straight (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss11 | green | sv13 | condition turnout (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss11 | green | sv15 | condition turnout (required), trigger co:soUTg=on | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss12 | green | gv01 | condition straight (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss12 | green | sv08 | condition straight (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss12 | green | sv08 | condition straight (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss12 | green | sv09 | condition turnout (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss12 | green | sv09 | condition turnout (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss12 | green | sv11 | condition straight (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss12 | green | sv11 | condition straight (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss12 | green | sv13 | condition straight (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss12 | green | sv13 | condition turnout (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss12 | green | sv15 | condition turnout (required), trigger co:soUTg=on | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss13 | green | gv01 | condition straight (required), trigger co:soUTg=on | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss13 | green | sv09 | condition straight (required), trigger co:soUTg=on | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss13 | green | sv09 | condition straight (required), trigger co:soUTg=on | sw:sv09=straight and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss13 | green | sv11 | condition straight (required), trigger co:soUTg=on | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss13 | green | sv11 | condition straight (required), trigger co:soUTg=on | sw:sv09=straight and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss13 | green | sv13 | condition straight (required), trigger co:soUTg=on | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss13 | green | sv13 | condition turnout (required), trigger co:soUTg=on | sw:sv09=straight and sw:sv11=straight and sw:sv13=turnout and fb:sd15=false and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss13 | green | sv15 | condition turnout (required), trigger co:soUTg=on | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| ss14 | green | gv01 | condition straight (required), trigger co:soUTm=on | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss14 | green | sv10 | condition straight (required), trigger co:soUTm=on | sw:sv10=straight and sw:sv11=straight and sw:sv13=straight and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss14 | green | sv10 | condition straight (required), trigger co:soUTm=on | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss14 | green | sv11 | condition straight (required), trigger co:soUTm=on | sw:sv10=straight and sw:sv11=straight and sw:sv13=straight and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss14 | green | sv11 | condition turnout (required), trigger co:soUTm=on | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss14 | green | sv13 | condition straight (required), trigger co:soUTm=on | sw:sv10=straight and sw:sv11=straight and sw:sv13=straight and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss14 | green | sv13 | condition straight (required), trigger co:soUTm=on | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss14 | green | sv15 | condition turnout (required), trigger co:soUTm=on | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss14 | red | sv11 | condition turnout (required), trigger sg:ss16=yellow | sw:sv11=turnout |
| ss15 | green | gv01 | condition straight (required), trigger co:soUTm=on | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss15 | green | sv10 | condition turnout (required), trigger co:soUTm=on | sw:sv10=turnout and sw:sv11=straight and sw:sv13=straight and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss15 | green | sv10 | condition turnout (required), trigger co:soUTm=on | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss15 | green | sv11 | condition straight (required), trigger co:soUTm=on | sw:sv10=turnout and sw:sv11=straight and sw:sv13=straight and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss15 | green | sv11 | condition turnout (required), trigger co:soUTm=on | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss15 | green | sv13 | condition straight (required), trigger co:soUTm=on | sw:sv10=turnout and sw:sv11=straight and sw:sv13=straight and fb:sd16=false and fb:gd05=false and fb:gd07=false and (fb:sd18=true or fb:sd19=true) |
| ss15 | green | sv13 | condition straight (required), trigger co:soUTm=on | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss15 | green | sv15 | condition turnout (required), trigger co:soUTm=on | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd16=false and fb:sd18=false and fb:sd19=false |
| ss15 | red | sv11 | condition turnout (required), trigger sg:ss16=yellow | sw:sv11=turnout |
| ss16 | green | sv09 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=straight and fb:sd15=false and fb:sd12=false |
| ss16 | green | sv11 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=straight and fb:sd15=false and fb:sd12=false |
| ss16 | green | sv13 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=straight and fb:sd15=false and fb:sd12=false |
| ss16 | green | sv15 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=straight and fb:sd15=false and fb:sd12=false |
| ss16 | yellow | sv08 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and fb:sd15=false and fb:sd11=false |
| ss16 | yellow | sv08 | condition turnout (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and fb:sd15=false and fb:sd10=false |
| ss16 | yellow | sv09 | condition turnout (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and fb:sd15=false and fb:sd11=false |
| ss16 | yellow | sv09 | condition turnout (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and fb:sd15=false and fb:sd10=false |
| ss16 | yellow | sv10 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and fb:sd15=false and fb:sd16=false and fb:sd13=false |
| ss16 | yellow | sv10 | condition turnout (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and fb:sd15=false and fb:sd16=false and fb:sd14=false |
| ss16 | yellow | sv11 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and fb:sd15=false and fb:sd11=false |
| ss16 | yellow | sv11 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and fb:sd15=false and fb:sd10=false |
| ss16 | yellow | sv11 | condition turnout (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and fb:sd15=false and fb:sd16=false and fb:sd13=false |
| ss16 | yellow | sv11 | condition turnout (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and fb:sd15=false and fb:sd16=false and fb:sd14=false |
| ss16 | yellow | sv13 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and fb:sd15=false and fb:sd11=false |
| ss16 | yellow | sv13 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and fb:sd15=false and fb:sd10=false |
| ss16 | yellow | sv13 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and fb:sd15=false and fb:sd16=false and fb:sd13=false |
| ss16 | yellow | sv13 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and fb:sd15=false and fb:sd16=false and fb:sd14=false |
| ss16 | yellow | sv15 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and fb:sd15=false and fb:sd11=false |
| ss16 | yellow | sv15 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and fb:sd15=false and fb:sd10=false |
| ss16 | yellow | sv15 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and fb:sd15=false and fb:sd16=false and fb:sd13=false |
| ss16 | yellow | sv15 | condition straight (required), trigger co:soINg=on | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and fb:sd15=false and fb:sd16=false and fb:sd14=false |
| ss17 | green | sv10 | condition straight (required), trigger sg:ss06=green | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | green | sv11 | condition turnout (required), trigger sg:ss06=green | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | green | sv13 | condition straight (required), trigger sg:ss06=green | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | green | sv15 | condition straight (required), trigger sg:ss06=green | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv08 | condition straight (required), trigger sg:ss08=green | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv08 | condition turnout (required), trigger sg:ss09=green | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv09 | condition straight (required), trigger sg:ss07=green | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv09 | condition turnout (required), trigger sg:ss08=green | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv09 | condition turnout (required), trigger sg:ss09=green | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv10 | condition straight (required), trigger sg:ss06=yellow | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv10 | condition turnout (required), trigger sg:ss05=green | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv11 | condition straight (required), trigger sg:ss07=green | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv11 | condition straight (required), trigger sg:ss08=green | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv11 | condition straight (required), trigger sg:ss09=green | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv11 | condition turnout (required), trigger sg:ss05=green | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv11 | condition turnout (required), trigger sg:ss06=yellow | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv13 | condition straight (required), trigger sg:ss05=green | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv13 | condition straight (required), trigger sg:ss06=yellow | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv13 | condition straight (required), trigger sg:ss07=green | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv13 | condition straight (required), trigger sg:ss08=green | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv13 | condition straight (required), trigger sg:ss09=green | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv15 | condition straight (required), trigger sg:ss05=green | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv15 | condition straight (required), trigger sg:ss06=yellow | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv15 | condition straight (required), trigger sg:ss07=green | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv15 | condition straight (required), trigger sg:ss08=green | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | sv15 | condition straight (required), trigger sg:ss09=green | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss20 | green | sv11 | condition straight (required), trigger sg:ss14=green | sw:sv11=straight |
| ss20 | yellow | sv11 | condition turnout (required), trigger sg:ss14=green | sw:sv11=turnout |
| ss23 | green | sv01 | condition straight (required), trigger sg:ss06=green | sw:sv01=straight |
| ss23 | yellow | sv01 | condition turnout (required), trigger sg:ss06=green | sw:sv01=turnout |
| ss25 | green | sv06 | condition turnout (required), trigger sg:ss09=green | sw:sv06=turnout |
| ss25 | green | sv06 | condition turnout (required), trigger sg:ss10=green | sw:sv06=turnout |
| ss25 | red | sv06 | condition turnout (required), trigger sg:ss09=red | sw:sv06=turnout |
| ss25 | red | sv06 | condition turnout (required), trigger sg:ss10=red | sw:sv06=turnout |
| ss26 | green | sv06 | condition straight (required), trigger co:soINi=on | sw:sv06=straight and sw:sv07=straight and fb:sd10=false |
| ss26 | green | sv06 | condition straight (required), trigger co:soINi=on | sw:sv06=straight and sw:sv07=turnout and fb:sd17=false |
| ss26 | green | sv07 | condition straight (required), trigger co:soINi=on | sw:sv06=straight and sw:sv07=straight and fb:sd10=false |
| ss26 | green | sv07 | condition turnout (required), trigger co:soINi=on | sw:sv06=straight and sw:sv07=turnout and fb:sd17=false |
| ss28 | green | sv01 | condition turnout (required), trigger co:soINi=on | sw:sv01=turnout and fb:sd09=false |

### 2. Sensors that stop signals from showing proceed

Sensor conditions on green/yellow/white actions, and red actions triggered when a sensor goes occupied.

| Signal | Aspect | Sensor | Block | How |
|---|---|---|---|---|
| ss01 | green | sd09 |  | must be free; trigger co:soINi=on |
| ss01 | green | sd13 |  | must be free; trigger co:soINi=on |
| ss01 | yellow | sd09 |  | must be free; trigger co:soINi=on |
| ss01 | yellow | sd10 |  | must be free; trigger co:soINi=on |
| ss01 | yellow | sd11 |  | must be free; trigger co:soINi=on |
| ss01 | yellow | sd12 |  | must be free; trigger co:soINi=on |
| ss01 | yellow | sd14 |  | must be free; trigger co:soINi=on |
| ss01 | yellow | sd17 |  | must be free; trigger co:soINi=on |
| ss05 | green | sd09 |  | must be free; trigger co:soUTi=on |
| ss06 | green | sd09 |  | must be free; trigger co:soUTi=on |
| ss07 | green | sd09 |  | must be free; trigger co:soUTi=on |
| ss08 | green | sd09 |  | must be free; trigger co:soUTi=on |
| ss09 | green | sd09 |  | must be free; trigger co:soUTi=on |
| ss10 | green | sd09 |  | must be free; trigger co:soUTi=on |
| ss11 | green | gd05 |  | must be free; trigger co:soUTg=on |
| ss11 | green | gd07 |  | must be free; trigger co:soUTg=on |
| ss11 | green | sd15 |  | must be free; trigger co:soUTg=on |
| ss11 | green | sd16 |  | must be free; trigger co:soUTg=on |
| ss11 | green | sd18 |  | must be free; trigger co:soUTg=on |
| ss11 | green | sd19 |  | must be free; trigger co:soUTg=on |
| ss12 | green | gd05 |  | must be free; trigger co:soUTg=on |
| ss12 | green | gd07 |  | must be free; trigger co:soUTg=on |
| ss12 | green | sd15 |  | must be free; trigger co:soUTg=on |
| ss12 | green | sd16 |  | must be free; trigger co:soUTg=on |
| ss12 | green | sd18 |  | must be free; trigger co:soUTg=on |
| ss12 | green | sd19 |  | must be free; trigger co:soUTg=on |
| ss13 | green | gd05 |  | must be free; trigger co:soUTg=on |
| ss13 | green | gd07 |  | must be free; trigger co:soUTg=on |
| ss13 | green | sd15 |  | must be free; trigger co:soUTg=on |
| ss13 | green | sd16 |  | must be free; trigger co:soUTg=on |
| ss13 | green | sd18 |  | must be free; trigger co:soUTg=on |
| ss13 | green | sd19 |  | must be free; trigger co:soUTg=on |
| ss14 | green | gd05 |  | must be free; trigger co:soUTm=on |
| ss14 | green | gd07 |  | must be free; trigger co:soUTm=on |
| ss14 | green | sd15 |  | must be free; trigger co:soUTm=on |
| ss14 | green | sd16 |  | must be free; trigger co:soUTm=on |
| ss14 | green | sd18 |  | must be free; trigger co:soUTm=on |
| ss14 | green | sd19 |  | must be free; trigger co:soUTm=on |
| ss15 | green | gd05 |  | must be free; trigger co:soUTm=on |
| ss15 | green | gd07 |  | must be free; trigger co:soUTm=on |
| ss15 | green | sd15 |  | must be free; trigger co:soUTm=on |
| ss15 | green | sd16 |  | must be free; trigger co:soUTm=on |
| ss15 | green | sd18 |  | must be free; trigger co:soUTm=on |
| ss15 | green | sd19 |  | must be free; trigger co:soUTm=on |
| ss16 | green | sd12 |  | must be free; trigger co:soINg=on |
| ss16 | green | sd15 |  | must be free; trigger co:soINg=on |
| ss16 | yellow | sd10 |  | must be free; trigger co:soINg=on |
| ss16 | yellow | sd11 |  | must be free; trigger co:soINg=on |
| ss16 | yellow | sd13 |  | must be free; trigger co:soINg=on |
| ss16 | yellow | sd14 |  | must be free; trigger co:soINg=on |
| ss16 | yellow | sd15 |  | must be free; trigger co:soINg=on |
| ss16 | yellow | sd16 |  | must be free; trigger co:soINg=on |
| ss26 | green | sd10 |  | must be free; trigger co:soINi=on |
| ss26 | green | sd17 |  | must be free; trigger co:soINi=on |
| ss28 | green | sd09 |  | must be free; trigger co:soINi=on |

### 3.1 Signals triggered by other signals

| Signal | Aspect | Triggered by signal | When | Conditions |
|---|---|---|---|---|
| ss01 | red | ss16 | green | sw:sv04=straight and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | ss16 | yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=straight and sw:sv05=straight and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | ss16 | yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=straight and sw:sv09=turnout and sw:sv08=turnout and sw:sv07=straight and sw:sv06=turnout and sw:sv05=turnout and sw:sv04=turnout and sw:sv02=turnout and sw:sv01=straight |
| ss01 | red | ss16 | yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=straight and sw:sv03=straight and sw:sv02=straight and sw:sv01=straight |
| ss01 | red | ss16 | yellow | sw:sv15=straight and sw:sv13=straight and sw:sv11=turnout and sw:sv10=turnout and sw:sv03=turnout and sw:sv02=straight and sw:sv01=straight |
| ss05 | red | ss05 | yellow | - |
| ss06 | red | ss06 | yellow | - |
| ss07 | red | ss07 | yellow | - |
| ss08 | red | ss08 | yellow | - |
| ss09 | red | ss09 | yellow | - |
| ss10 | red | ss10 | yellow | - |
| ss11 | red | ss11 | yellow | - |
| ss11 | red | ss16 | yellow | - |
| ss12 | red | ss12 | yellow | - |
| ss12 | red | ss16 | yellow | - |
| ss13 | red | ss13 | yellow | - |
| ss13 | red | ss16 | green | - |
| ss14 | red | ss14 | yellow | - |
| ss14 | red | ss16 | yellow | sw:sv11=turnout |
| ss15 | red | ss15 | yellow | - |
| ss15 | red | ss16 | yellow | sw:sv11=turnout |
| ss17 | green | ss06 | green | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | red | ss05 | red | - |
| ss17 | red | ss06 | red | - |
| ss17 | red | ss07 | red | - |
| ss17 | red | ss08 | red | - |
| ss17 | red | ss09 | red | - |
| ss17 | red | ss16 | red | - |
| ss17 | yellow | ss05 | green | sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | ss06 | yellow | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | ss07 | green | sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | ss08 | green | sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss17 | yellow | ss09 | green | sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |
| ss18 | green | ss11 | green | - |
| ss18 | green | ss12 | green | - |
| ss18 | red | ss11 | red | - |
| ss18 | red | ss12 | red | - |
| ss19 | green | ss13 | green | - |
| ss19 | red | ss13 | yellow | - |
| ss20 | green | ss14 | green | sw:sv11=straight |
| ss20 | red | ss14 | yellow | - |
| ss20 | yellow | ss14 | green | sw:sv11=turnout |
| ss21 | green | ss15 | green | - |
| ss21 | red | ss15 | yellow | - |
| ss22 | green | ss05 | green | - |
| ss22 | red | ss05 | yellow | - |
| ss23 | green | ss06 | green | sw:sv01=straight |
| ss23 | red | ss06 | yellow | - |
| ss23 | yellow | ss06 | green | sw:sv01=turnout |
| ss24 | green | ss07 | green | - |
| ss24 | red | ss07 | yellow | - |
| ss25 | green | ss08 | green | - |
| ss25 | green | ss09 | green | sw:sv06=turnout |
| ss25 | green | ss10 | green | sw:sv06=turnout |
| ss25 | red | ss08 | red | - |
| ss25 | red | ss09 | red | sw:sv06=turnout |
| ss25 | red | ss10 | red | sw:sv06=turnout |
| ss26 | red | ss26 | yellow | - |
| ss27 | green | ss28 | green | - |
| ss27 | red | ss28 | red | - |
| ss29 | green | ss16 | green | - |
| ss29 | red | ss16 | red | - |
| ss29 | yellow | ss16 | yellow | - |

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| sd18 | fb | sd18off | off | co:dirRes=on | - |  |
| sd19 | fb | sd19off | off | co:dirRes=on | - |  |
| soINg | co | soINgOff | off | co:soUTg=on | co:soINg=on |  |
| soINg | co | soINgOff | off | co:soUTm=on | co:soINg=on |  |
| soINg | co | soINgOff | off | fb:sd07=true | sw:sv13=turnout |  |
| soINg | co | soINgOff | off | fb:sd15=true | co:soINg=on |  |
| soINg | co | soINgOff | off | sg:ss01=green | sw:sv10=straight and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |  |
| soINg | co | soINgOff | off | sg:ss01=yellow | sw:sv02=straight and sw:sv03=turnout and sw:sv10=turnout and sw:sv11=turnout and sw:sv13=straight and sw:sv15=straight |  |
| soINg | co | soINgOff | off | sg:ss01=yellow | sw:sv02=turnout and sw:sv04=straight and sw:sv09=straight and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |  |
| soINg | co | soINgOff | off | sg:ss01=yellow | sw:sv02=turnout and sw:sv04=turnout and sw:sv05=straight and sw:sv08=straight and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |  |
| soINg | co | soINgOff | off | sg:ss01=yellow | sw:sv02=turnout and sw:sv04=turnout and sw:sv05=turnout and sw:sv06=turnout and sw:sv07=straight and sw:sv08=turnout and sw:sv09=turnout and sw:sv11=straight and sw:sv13=straight and sw:sv15=straight |  |
| soINg | co | soINgOff | off | sw:sv11=any | - |  |
| soINg | co | soINgOff | off | sw:sv13=any | co:soINg=on |  |
| soINg | co | soINgOff | off | sw:sv15=any | co:soINg=on |  |
| soINg | co | soINgOn | on | fb:sd07=true | sw:sv13=straight |  |
| soINi | co | soINiOff | off | co:soUTi=on | co:soINi=on |  |
| soINi | co | soINiOff | off | fb:sd09=true | co:soINi=on |  |
| soINi | co | soINiOff | off | sw:sv01=any | co:soINi=on |  |
| soINi | co | soINiOff | off | sw:sv02=any | - |  |
| soINi | co | soINiOff | off | sw:sv03=any | sw:sv02=straight |  |
| soINi | co | soINiOff | off | sw:sv04=any | sw:sv02=turnout |  |
| soINi | co | soINiOff | off | sw:sv05=any | sw:sv02=turnout and sw:sv04=turnout |  |
| soINi | co | soINiOff | off | sw:sv06=any | (sg:ss09=green or sg:ss10=green or sg:ss26=green) |  |
| soINi | co | soINiOff | off | sw:sv07=any | (sg:ss09=green or sg:ss10=green or sg:ss26=green) |  |
| soINi | co | soINiOn | on | fb:sd06=true | - |  |
| soUTg | co | soUTgOff | off | co:soINg=on | co:soUTg=on |  |
| soUTg | co | soUTgOff | off | fb:sd15=true | co:soUTg=on |  |
| soUTg | co | soUTgOff | off | sw:sv08=any | - |  |
| soUTg | co | soUTgOff | off | sw:sv09=any | - |  |
| soUTg | co | soUTgOff | off | sw:sv11=any | - |  |
| soUTg | co | soUTgOff | off | sw:sv13=any | co:soUTg=on |  |
| soUTg | co | soUTgOff | off | sw:sv15=any | co:soUTg=on |  |
| soUTg | co | soUTgOn | on | fb:sd08=true | - |  |
| soUTi | co | soUTiOff | off | co:soINi=on | co:soUTi=on |  |
| soUTi | co | soUTiOff | off | fb:sd09=true | co:soUTi=on |  |
| soUTi | co | soUTiOff | off | sw:sv01=any | co:soUTi=on |  |
| soUTi | co | soUTiOff | off | sw:sv02=any | - |  |
| soUTi | co | soUTiOff | off | sw:sv03=any | sw:sv02=straight |  |
| soUTi | co | soUTiOff | off | sw:sv04=any | sw:sv02=turnout |  |
| soUTi | co | soUTiOff | off | sw:sv05=any | sw:sv02=turnout and sw:sv04=turnout |  |
| soUTi | co | soUTiOff | off | sw:sv06=any | (sg:ss09=green or sg:ss10=green or sg:ss26=green) |  |
| soUTi | co | soUTiOff | off | sw:sv07=any | (sg:ss09=green or sg:ss10=green or sg:ss26=green) |  |
| soUTi | co | soUTiOn | on | fb:sd05=true | - |  |
| soUTm | co | soUTmOff | off | co:soINg=on | co:soUTm=on |  |
| soUTm | co | soUTmOff | off | fb:sd15=true | co:soUTm=on and sw:sv11=turnout |  |
| soUTm | co | soUTmOff | off | fb:sd16=true | co:soUTm=on |  |
| soUTm | co | soUTmOff | off | sw:sv10=any | - |  |
| soUTm | co | soUTmOff | off | sw:sv11=any | - |  |
| soUTm | co | soUTmOff | off | sw:sv13=any | co:soUTm=on |  |
| soUTm | co | soUTmOff | off | sw:sv15=any | co:soUTm=on and sw:sv13=straight and sw:sv11=turnout |  |
| soUTm | co | soUTmOn | on | fb:sd08=true | - |  |
| stxDir | tx | stxDirHavna | update | fb:sd18=true | fb:sd19=true |  |
| stxDir | tx | stxDirHavna | update | fb:sd19=true | fb:sd18=true |  |
| stxDir | tx | stxDirMjd | update | fb:sd18=false | fb:sd19=true |  |
| stxDir | tx | stxDirMjd | update | fb:sd19=true | fb:sd18=false |  |
| stxDir | tx | stxDirSigdal | update | fb:sd18=true | fb:sd19=false |  |
| stxDir | tx | stxDirSigdal | update | fb:sd19=false | fb:sd18=true |  |
| stxDir | tx | stxDirSkifte | update | fb:sd18=false | fb:sd19=false |  |
| stxDir | tx | stxDirSkifte | update | fb:sd19=false | fb:sd18=false |  |
| sv11 | sw | sv11straight | straight | sw:sv12=straight | sw:sv11=turnout |  |
| sv11 | sw | sv11turnout | turnout | sw:sv12=turnout | sw:sv11=straight |  |
| sv12 | sw | sv12straight | straight | sw:sv11=straight | sw:sv12=turnout |  |
| sv12 | sw | sv12turnout | turnout | sw:sv11=turnout | sw:sv12=straight |  |
| sv13 | sw | sv13straight | straight | sw:sv14=straight | sw:sv13=turnout |  |
| sv13 | sw | sv13turnout | turnout | sw:sv14=turnout | sw:sv13=straight |  |
| sv14 | sw | sv14straight | straight | sw:sv13=straight | sw:sv14=turnout |  |
| sv14 | sw | sv14turnout | turnout | sw:sv13=turnout | sw:sv14=straight |  |

## Solberg Skiftegård (g)

### 1. Turnouts that affect signals

| Signal | Aspect | Turnout | How | Full condition |
|---|---|---|---|---|
| gs03 | green | gv01 | condition straight (required), trigger sg:gs04=green | sw:gv01=straight and sw:sv15=turnout and sw:sv13=straight |
| gs03 | green | sv13 | condition straight (required), trigger sg:gs04=green | sw:gv01=straight and sw:sv15=turnout and sw:sv13=straight |
| gs03 | green | sv15 | condition turnout (required), trigger sg:gs04=green | sw:gv01=straight and sw:sv15=turnout and sw:sv13=straight |
| gs04 | yellow | gv01 | condition straight (required), trigger co:soINg=off | sg:gs04=green and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | gv01 | condition straight (required), trigger co:soUTg=on | sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| gs04 | yellow | gv01 | condition straight (required), trigger sw:sv11=any | sg:gs04=green and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | gv01 | condition straight (required), trigger sw:sv13=any | sg:gs04=green and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | gv01 | condition straight (required), trigger sw:sv15=any | sg:gs04=green and sw:gv01=straight |
| gs04 | yellow | gv01 | condition turnout (required), trigger co:goUTsTmr=on | sw:gv01=turnout and sg:gs04=green |
| gs04 | yellow | gv01 | trigger when any | sg:gs04=green |
| gs04 | yellow | gv02 | condition turnout (required), trigger sw:gv03=any | sg:gs04=green and sw:gv02=turnout |
| gs04 | yellow | gv02 | trigger when any | sg:gs04=green |
| gs04 | yellow | gv03 | trigger when any | sg:gs04=green and sw:gv02=turnout |
| gs04 | yellow | sv11 | trigger when any | sg:gs04=green and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | sv13 | condition straight (required), trigger co:soUTg=on | sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| gs04 | yellow | sv13 | condition straight (required), trigger sw:sv11=any | sg:gs04=green and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | sv13 | trigger when any | sg:gs04=green and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | sv15 | condition turnout (required), trigger co:soINg=off | sg:gs04=green and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | sv15 | condition turnout (required), trigger co:soUTg=on | sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |
| gs04 | yellow | sv15 | condition turnout (required), trigger sw:sv11=any | sg:gs04=green and sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | sv15 | condition turnout (required), trigger sw:sv13=any | sg:gs04=green and sw:sv15=turnout and sw:gv01=straight |
| gs04 | yellow | sv15 | trigger when any | sg:gs04=green and sw:gv01=straight |
| gs05 | green | gv02 | condition straight (required), trigger co:goUTs=on | sw:gv02=straight and fb:gd01=false |
| gs06 | green | gv02 | condition turnout (required), trigger co:goUTs=on | sw:gv02=turnout and sw:gv03=straight and fb:gd01=false |
| gs06 | green | gv03 | condition straight (required), trigger co:goUTs=on | sw:gv02=turnout and sw:gv03=straight and fb:gd01=false |
| gs07 | green | gv02 | condition turnout (required), trigger co:goUTs=on | sw:gv02=turnout and sw:gv03=turnout and fb:gd01=false |
| gs07 | green | gv03 | condition turnout (required), trigger co:goUTs=on | sw:gv02=turnout and sw:gv03=turnout and fb:gd01=false |
| gs08 | green | gv04 | condition turnout (required), trigger co:goUTk=on | sw:gv04=turnout and sw:gv05=turnout and fb:gd06=false |
| gs08 | green | gv05 | condition turnout (required), trigger co:goUTk=on | sw:gv04=turnout and sw:gv05=turnout and fb:gd06=false |
| gs09 | green | gv04 | condition straight (required), trigger co:goUTk=on | sw:gv04=straight and sw:gv05=turnout and fb:gd06=false |
| gs09 | green | gv05 | condition turnout (required), trigger co:goUTk=on | sw:gv04=straight and sw:gv05=turnout and fb:gd06=false |
| gs10 | green | gv05 | condition straight (required), trigger co:goUTk=on | sw:gv05=straight and fb:gd06=false |
| gs11 | green | gv06 | condition straight (required), trigger sg:gs08=green | sw:gv06=straight and sg:gs11=red |
| gs11 | green | gv06 | condition straight (required), trigger sg:gs09=green | sw:gv06=straight and sg:gs11=red |
| gs11 | green | gv06 | condition straight (required), trigger sg:gs10=green | sw:gv06=straight and sg:gs11=red |
| gs11 | red | gv06 | condition straight (required), trigger fb:kd01=true | sw:gv06=straight and sg:gs11=green |
| gs11 | red | gv06 | condition turnout (required), trigger sg:gs08=green | sw:gv06=turnout and sg:gs11=green |
| gs11 | red | gv06 | condition turnout (required), trigger sg:gs09=green | sw:gv06=turnout and sg:gs11=green |
| gs11 | red | gv06 | condition turnout (required), trigger sg:gs10=green | sw:gv06=turnout and sg:gs11=green |
| gs11 | red | gv06 | trigger when any | sg:gs11=green |

### 2. Sensors that stop signals from showing proceed

Sensor conditions on green/yellow/white actions, and red actions triggered when a sensor goes occupied.

| Signal | Aspect | Sensor | Block | How |
|---|---|---|---|---|
| gs04 | yellow | sd15 |  | must be free; trigger co:soUTg=on |
| gs04 | yellow | sd18 |  | must be free; trigger co:soUTg=on |
| gs04 | yellow | sd19 |  | must be free; trigger co:soUTg=on |
| gs05 | green | gd01 |  | must be free; trigger co:goUTs=on |
| gs06 | green | gd01 |  | must be free; trigger co:goUTs=on |
| gs07 | green | gd01 |  | must be free; trigger co:goUTs=on |
| gs08 | green | gd06 |  | must be free; trigger co:goUTk=on |
| gs09 | green | gd06 |  | must be free; trigger co:goUTk=on |
| gs10 | green | gd06 |  | must be free; trigger co:goUTk=on |
| gs11 | red | kd01 |  | occupied sets red; condition sw:gv06=straight and sg:gs11=green |

### 2.1 Routes that set signals

Rocrail sets these aspects only when it can lock the route, so an occupied destination block stops them.

| Signal | Aspect when set | Route | From -> to block |
|---|---|---|---|
| gs02 | green | krt-si | s4 -> k1 |
| gs02 | yellow | krt-sh | s4 -> k1 |
| gs02 | yellow | krt-sm | s4 -> k1 |

### 3.1 Signals triggered by other signals

| Signal | Aspect | Triggered by signal | When | Conditions |
|---|---|---|---|---|
| gs01 | green | gs02 | green | - |
| gs01 | red | gs02 | red | - |
| gs01 | yellow | gs02 | yellow | - |
| gs03 | green | gs04 | green | sw:gv01=straight and sw:sv15=turnout and sw:sv13=straight |
| gs03 | red | gs04 | any | sg:gs03=green |
| gs04 | green | gs05 | green | - |
| gs04 | green | gs06 | green | - |
| gs04 | green | gs07 | green | - |
| gs04 | red | gs04 | yellow | - |
| gs05 | red | gs05 | yellow | - |
| gs06 | red | gs06 | yellow | - |
| gs07 | red | gs07 | yellow | - |
| gs08 | red | gs08 | yellow | - |
| gs09 | red | gs09 | yellow | - |
| gs10 | red | gs10 | yellow | - |
| gs11 | green | gs08 | green | sw:gv06=straight and sg:gs11=red |
| gs11 | green | gs09 | green | sw:gv06=straight and sg:gs11=red |
| gs11 | green | gs10 | green | sw:gv06=straight and sg:gs11=red |
| gs11 | red | gs08 | green | sw:gv06=turnout and sg:gs11=green |
| gs11 | red | gs09 | green | sw:gv06=turnout and sg:gs11=green |
| gs11 | red | gs10 | green | sw:gv06=turnout and sg:gs11=green |

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| gd06d | co | gd06dOff | off | fb:gd06=false | - |  |
| gd06d | co | gd06dOn | on | co:gd06d=off | fb:gd06=true |  |
| gd06d | co | gd06dOn | on | fb:gd06=true | - |  |
| gd10 | fb | gd10off | off | co:dirRes=on | - |  |
| gd10 | fb | gd10off | off | fb:gd11=true | - |  |
| gd11 | fb | gd11off | off | co:dirRes=on | - |  |
| gd11 | fb | gd11off | off | fb:gd10=true | - |  |
| goUTk | co | goUTkOff | off | co:koCtl=off | co:goUTk=on |  |
| goUTk | co | goUTkOff | off | fb:gd06=true | - |  |
| goUTk | co | goUTkOff | off | sw:gv06=any | co:goUTk=on |  |
| goUTk | co | goUTkOn | on | fb:gd09=true | sw:gv06=turnout |  |
| goUTkTmr | co | goUTkTmrOff | off | co:goUTkTmr=on | - |  |
| goUTkTmr | co | goUTkTmrOn | on | sg:gs08=yellow | sg:gs11=green |  |
| goUTkTmr | co | goUTkTmrOn | on | sg:gs09=yellow | sg:gs11=green |  |
| goUTkTmr | co | goUTkTmrOn | on | sg:gs10=yellow | sg:gs11=green |  |
| goUTs | co | goUTsOff | off | co:soUTg=on | sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight and fb:sd15=false and fb:sd18=false and fb:sd19=false |  |
| goUTs | co | goUTsOff | off | fb:gd01=any | co:goUTs=on |  |
| goUTs | co | goUTsOff | off | fb:sd15=true | co:goUTs=on and sw:sv15=turnout and sw:gv01=straight |  |
| goUTs | co | goUTsOff | off | sg:gs04=red | co:goUTs=on |  |
| goUTs | co | goUTsOff | off | sw:gv01=any | co:goUTs=on |  |
| goUTs | co | goUTsOff | off | sw:gv02=any | co:goUTs=on |  |
| goUTs | co | goUTsOff | off | sw:gv03=any | co:goUTs=on and sw:gv02=turnout |  |
| goUTs | co | goUTsOff | off | sw:sv11=any | sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight |  |
| goUTs | co | goUTsOff | off | sw:sv13=any | sw:sv15=turnout and sw:gv01=straight |  |
| goUTs | co | goUTsOff | off | sw:sv15=any | sw:gv01=straight |  |
| goUTs | co | goUTsOn | on | fb:gd08=true | sw:gv01=turnout |  |
| goUTs | co | goUTsOn | on | fb:sd07=true | sw:sv13=straight and sw:sv15=turnout and sw:gv01=straight |  |
| goUTsTmr | co | goUTsTmrOff | off | co:goUTsTmr=on | - |  |
| goUTsTmr | co | goUTsTmrOn | on | sg:gs05=yellow | sw:gv01=turnout and sg:gs04=green |  |
| goUTsTmr | co | goUTsTmrOn | on | sg:gs06=yellow | sw:gv01=turnout and sg:gs04=green |  |
| goUTsTmr | co | goUTsTmrOn | on | sg:gs07=yellow | sw:gv01=turnout and sg:gs04=green |  |
| gtxDir | tx | gtxDirHavna | update | fb:gd11=true | fb:gd10=false |  |
| gtxDir | tx | gtxDirMjd | update | fb:gd10=false | fb:gd11=false |  |
| gtxDir | tx | gtxDirMjd | update | fb:gd11=false | fb:gd10=false |  |
| gtxDir | tx | gtxDirSigdal | update | fb:gd10=true | fb:gd11=false |  |

## Kobbarvik (k)

### 2. Sensors that stop signals from showing proceed

Sensor conditions on green/yellow/white actions, and red actions triggered when a sensor goes occupied.

| Signal | Aspect | Sensor | Block | How |
|---|---|---|---|---|
| ks02 | red | kd05 |  | occupied sets red; condition sg:ks02=green |

### 2.1 Routes that set signals

Rocrail sets these aspects only when it can lock the route, so an occupied destination block stops them.

| Signal | Aspect when set | Route | From -> to block |
|---|---|---|---|
| ks01 | green | krt-is | i2 -> s3 |
| ks01 | yellow | krt-ig | i2 -> k1 |
| ks02 | green | krt-mg | m2 -> k1 |
| ks02 | green | krt-ms | m2 -> s3 |
| ks03 | green | krt-hg | h1 -> k1 |
| ks03 | yellow | krt-hs | h1 -> s3 |

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| koCtl | co | koCtlOff | off | co:koCtl=on | co:krt-busy=off |  |
| koCtl | co | koCtlOff | off | co:koOcc=off | - |  |
| koCtl | co | koCtlOff | off | sw:gv06=any | co:koOcc=off and fb:gd06=false and (st:krt-gi=locked or st:krt-gm=locked or st:krt-gh=locked) |  |
| koCtl | co | koCtlOn | on | co:koCtl=off | (co:koRTgp=on or co:koRTip=on or co:koRTsp=on or co:koRTmp=on or co:koRThp=on) |  |
| koCtl | co | koCtlOn | on | co:koRTgp=on | co:koCtl=off |  |
| koCtl | co | koCtlOn | on | co:koRThp=on | co:koCtl=off |  |
| koCtl | co | koCtlOn | on | co:koRTip=on | co:koCtl=off |  |
| koCtl | co | koCtlOn | on | co:koRTmp=on | co:koCtl=off |  |
| koCtl | co | koCtlOn | on | co:koRTsp=on | co:koCtl=off |  |
| koLF | co | koLFoff | off | co:koLFlok=on | - |  |
| koLF | co | koLFon | on | co:koCtl=on | co:koLFlok=off and co:krt-busy=on |  |
| koOcc | co | koOccOff | off | co:koOcc=on | fb:kd07=false and vr:koOccTmr=>4 and (st:krt-is=locked or st:krt-ig=locked) | fra i |
| koOcc | co | koOccOff | off | co:koOcc=on | st:krt-is=unlocked and st:krt-is=unlocked and vr:koOccTmr=>2 | fra s, g, m |
| koOcc | co | koOccOff | off | fb:hd03=true | fb:hd01=false and fb:kd09=false and (st:krt-hg=locked or st:krt-hs=locked) |  |
| koOcc | co | koOccOff | off | fb:md09=true | fb:md01=false and fb:kd06=false and fb:kd05=false and (st:krt-mg=locked or st:krt-ms=locked) |  |
| koOcc | co | koOccOn | on | co:koOccT=on | co:koOcc=on |  |
| koOcc | co | koOccOn | on | fb:kd01=true | co:koOcc=off and fb:kd02=true |  |
| koOcc | co | koOccOn | on | fb:kd02=true | co:koOcc=off and (fb:kd01=true or fb:kd03=true or fb:kd04=true or fb:kd05=true) |  |
| koOcc | co | koOccOn | on | fb:kd03=true | co:koOcc=off and fb:kd02=true |  |
| koOcc | co | koOccOn | on | fb:kd04=true | co:koOcc=off and fb:kd02=true |  |
| koOcc | co | koOccOn | on | fb:kd05=true | co:koOcc=off and fb:kd02=true |  |
| koOcc | co | koOccOn | on | sw:mv01=any | fb:md01=false and fb:kd06=false and fb:kd05=false and (st:krt-mg=locked or st:krt-ms=locked) |  |
| koOccT | co | koOccTOff | off | co:koOcc=on | co:koOccT=off |  |
| koOccT | co | koOccTOff | off | co:koOccT=on | - |  |
| koOccT | co | koOccTOn | on | co:koOccT=off | co:koOcc=on |  |
| koOccTmr | vr | koOccTmrCnt | add | co:koOcc=on | fb:kd01=false and fb:kd02=false and fb:kd03=false and fb:kd04=false and fb:kd05=false |  |
| koOccTmr | vr | koOccTmrRes | value | co:koOcc=on | (fb:kd01=true or fb:kd02=true or fb:kd03=true or fb:kd04=true or fb:kd05=true) |  |
| koRTgdh | co | koRTgdhOff | off | co:koRTgp=on | fb:gd11=false |  |
| koRTgdh | co | koRTgdhOn | on | co:koRTgp=on | fb:gd10=false and fb:gd11=true |  |
| koRTgdi | co | koRTgdiOff | off | co:koRTgp=on | fb:gd10=false |  |
| koRTgdi | co | koRTgdiOn | on | co:koRTgp=on | fb:gd10=true and fb:gd11=false |  |
| koRTgp | co | koRTgpOff | off | st:krt-gh=lock | - |  |
| koRTgp | co | koRTgpOff | off | st:krt-gi=lock | - |  |
| koRTgp | co | koRTgpOff | off | st:krt-gm=lock | - |  |
| koRTgp | co | koRTgpOff | off | sw:gv06=any | - |  |
| koRTgp | co | koRTgpOn | on | fb:gd09=true | sw:gv06=straight and st:krt-hg=unlocked and st:krt-ig=unlocked and st:krt-mg=unlocked and st:krt-gh=unlocked and st:krt-gi=unlocked and st:krt-gm=unlocked |  |
| koRThd | co | koRThdOff | off | co:koRThp=on | fb:hd02=false |  |
| koRThd | co | koRThdOn | on | co:koRThp=on | fb:hd02=true |  |
| koRThp | co | koRThpOff | off | fb:hd02=false | fb:hd01=false and fb:kd09=false |  |
| koRThp | co | koRThpOff | off | fb:hd02=true | fb:hd01=false and fb:kd09=false |  |
| koRThp | co | koRThpOff | off | st:krt-hg=lock | - |  |
| koRThp | co | koRThpOff | off | st:krt-hs=lock | - |  |
| koRThp | co | koRThpOn | on | fb:hd03=on | st:krt-hg=unlocked and st:krt-hs=unlocked and st:krt-gh=unlocked and st:krt-sh=unlocked |  |
| koRTid | co | koRTidOff | off | co:koRTip=on | fb:id20=false and fb:id21=false |  |
| koRTid | co | koRTidOn | on | co:koRTip=on | fb:id20=true and fb:id21=false |  |
| koRTip | co | koRTipOff | off | fb:id16=true | fb:id21=true and sw:yv05=turnout |  |
| koRTip | co | koRTipOff | off | st:krt-ig=lock | - |  |
| koRTip | co | koRTipOff | off | st:krt-is=lock | - |  |
| koRTip | co | koRTipOff | off | sw:iv01=any | (st:krt-is=locked or st:krt-ig=locked) |  |
| koRTip | co | koRTipOff | off | sw:iv01=any | st:krt-is=unlocked and st:krt-is=unlocked and fb:kd07=false and sg:ys04=red |  |
| koRTip | co | koRTipOff | off | sw:yv05=any | (st:krt-is=locked or st:krt-ig=locked) |  |
| koRTip | co | koRTipOff | off | sw:yv05=any | st:krt-is=unlocked and st:krt-ig=unlocked and fb:kd07=false |  |
| koRTip | co | koRTipOff | off | sw:yv06=any | (st:krt-is=locked or st:krt-ig=locked) |  |
| koRTip | co | koRTipOff | off | sw:yv06=any | st:krt-is=unlocked and st:krt-ig=unlocked and fb:kd07=false and sg:ys04=red |  |
| koRTip | co | koRTipOn | on | fb:id16=true | fb:id21=false and sw:yv05=turnout and st:krt-is=unlocked and st:krt-ig=unlocked and st:krt-ki=unlocked |  |
| koRTmd | co | koRTmdOff | off | co:koRTmp=on | fb:md14=false |  |
| koRTmd | co | koRTmdOn | on | co:koRTmp=on | fb:md14=true |  |
| koRTmp | co | koRTmpOff | off | co:koCtl=on | co:krt-busy=off and co:koRTgp=on and co:koRTgdi=off and co:koRTgdh=off and co:koRTmp=on and fb:md01=false and fb:kd06=false | slett mp om g mot m er klar |
| koRTmp | co | koRTmpOff | off | co:koCtl=on | co:krt-busy=off and co:koRTsp=on and co:koRTsdi=off and co:koRTsdh=off and co:koRTmp=on and fb:md01=false and fb:kd06=false and (fb:gd05=true or fb:gd07=true) | slett mp om s mot m er klar |
| koRTmp | co | koRTmpOff | off | co:moINk=on | - |  |
| koRTmp | co | koRTmpOff | off | co:moSki=on | - |  |
| koRTmp | co | koRTmpOff | off | st:krt-mg=lock | - |  |
| koRTmp | co | koRTmpOff | off | st:krt-ms=lock | - |  |
| koRTmp | co | koRTmpOff | off | sw:mv01=any | fb:kd06=false and fb:md01=false |  |
| koRTmp | co | koRTmpOn | on | fb:md09=on | co:moSki=off and st:krt-gm=unlocked and st:krt-sm=unlocked and st:krt-mg=unlocked and st:krt-ms=unlocked |  |
| koRTsdh | co | koRTsdhOff | off | co:koRTsp=on | (fb:sd18=false or fb:sd19=false) |  |
| koRTsdh | co | koRTsdhOn | on | co:koRTsp=on | fb:sd18=true and fb:sd19=true |  |
| koRTsdi | co | koRTsdiOff | off | co:koRTsp=on | (fb:sd18=false or fb:sd19=true) |  |
| koRTsdi | co | koRTsdiOn | on | co:koRTsp=on | fb:sd18=true and fb:sd19=false |  |
| koRTsp | co | koRTspOff | off | st:krt-sh=lock | - |  |
| koRTsp | co | koRTspOff | off | st:krt-si=lock | - |  |
| koRTsp | co | koRTspOff | off | st:krt-sm=lock | - |  |
| koRTsp | co | koRTspOff | off | sw:sv11=any | fb:gd05=false and fb:gd07=false |  |
| koRTsp | co | koRTspOff | off | sw:sv13=any | fb:gd05=false and fb:gd07=false |  |
| koRTsp | co | koRTspOn | on | fb:sd08=true | sw:sv12=straight and st:krt-si=unlocked and st:krt-sm=unlocked and st:krt-sh=unlocked and (fb:sd18=true or fb:sd19=true) |  |
| krt-busy | co | krt-busyOff | off | co:koCtl=off | - |  |
| krt-busy | co | krt-busyOff | off | co:koCtl=on | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-gh=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-gi=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-gm=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-hg=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-hs=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-ig=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-is=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-mg=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-ms=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-sh=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-si=lock | - |  |
| krt-busy | co | krt-busyOn | on | st:krt-sm=lock | - |  |
| krt-gh | st | krt-ghFree | unlock | co:koCtl=off | st:krt-gh=locked |  |
| krt-gh | st | krt-ghSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTgp=on and co:koRTgdi=off and co:koRTgdh=on and co:koRThp=off and fb:kd09=false | g mot h |
| krt-gi | st | krt-giFree | unlock | co:koCtl=off | st:krt-gi=locked |  |
| krt-gi | st | krt-giSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTgp=on and co:koRTgdi=on and co:koRTgdh=off and st:krt-ki=unlocked and st:nrt-in-i1=unlocked and st:nrt-u2-ut=unlocked and co:yd03d=off | g mot i |
| krt-gm | st | krt-gmFree | unlock | co:koCtl=off | st:krt-gm=locked |  |
| krt-gm | st | krt-gmSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTgp=on and co:koRTgdi=off and co:koRTgdh=off and co:koRTmp=off and fb:md01=false and fb:kd06=false | g mot m |
| krt-hg | st | krt-hgFree | unlock | co:koCtl=off | st:krt-hg=locked |  |
| krt-hg | st | krt-hgSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRThp=on and co:koRThd=on and fb:gd06=false and sw:gv06=straight and sg:gs11=red and (fb:hd01=true or fb:kd09=true) | h mot g |
| krt-hs | st | krt-hsFree | unlock | co:koCtl=off | st:krt-hs=locked |  |
| krt-hs | st | krt-hsSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRThp=on and co:koRThd=off and fb:gd04=false and (fb:hd01=true or fb:kd09=true) | h mot s |
| krt-ig | st | krt-igFree | unlock | co:koCtl=off | st:krt-ig=locked |  |
| krt-ig | st | krt-igSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTip=on and co:koRTid=on and fb:gd06=false and sw:gv06=straight and sg:gs11=red and (fb:yd04=true or fb:kd07=true) | i mot g |
| krt-is | st | krt-isFree | unlock | co:koCtl=off | st:krt-is=locked |  |
| krt-is | st | krt-isSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTip=on and co:koRTid=off and fb:gd04=false and (fb:yd04=true or fb:kd07=true) | i mot s |
| krt-ki | st | krt-kiFree | unlock | co:yd03d=off | fb:yd03=false and st:krt-ki=locked and st:krt-gi=unlocked and st:krt-si=unlocked |  |
| krt-ki | st | krt-kiFree | unlock | vr:krt-kiTmr=>1 | fb:kd08=false and co:yd03d=off |  |
| krt-ki | st | krt-kiSet | lockset | st:krt-gi=lock | - |  |
| krt-ki | st | krt-kiSet | lockset | st:krt-si=lock | - |  |
| krt-kiTmr | vr | krt-kiTmrRes | value | vr:krt-kiTmr=>0 | (st:krt-gi=locked or st:krt-si=locked or fb:kd08=true or co:yd03d=on) |  |
| krt-kiTmr | vr | krt-kiTmrStart | start | st:krt-ki=lock | - |  |
| krt-kiTmr | vr | krt-kiTmrStop | stop | vr:krt-kiTmr=>1 | st:krt-ki=unlocked |  |
| krt-mg | st | krt-mgFree | unlock | co:koCtl=off | st:krt-mg=locked |  |
| krt-mg | st | krt-mgSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTmp=on and co:koRTmd=on and fb:gd06=false and sw:gv06=straight and sg:gs11=red and (fb:md01=true or fb:kd06=true) | m mot g |
| krt-ms | st | krt-msFree | unlock | co:koCtl=off | st:krt-ms=locked |  |
| krt-ms | st | krt-msSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTmp=on and co:koRTmd=off and fb:gd04=false and (fb:md01=true or fb:kd06=true) | m mot s |
| krt-sh | st | krt-shFree | unlock | co:koCtl=off | st:krt-sh=locked |  |
| krt-sh | st | krt-shSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTsp=on and co:koRTsdi=off and co:koRTsdh=on and co:koRThp=off and fb:kd09=false and (fb:gd05=true or fb:gd07=true) | s mot h |
| krt-si | st | krt-siFree | unlock | co:koCtl=off | st:krt-si=locked |  |
| krt-si | st | krt-siSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTsp=on and co:koRTsdi=on and co:koRTsdh=off and fb:kd08=false and st:krt-ki=unlocked and st:nrt-in-i1=unlocked and st:nrt-u2-ut=unlocked and co:yd03d=off and (fb:gd05=true or fb:gd07=true) | s mot i |
| krt-sm | st | krt-smFree | unlock | co:koCtl=off | st:krt-sm=locked |  |
| krt-sm | st | krt-smSet | lockset | co:koCtl=on | co:krt-busy=off and co:koRTsp=on and co:koRTsdi=off and co:koRTsdh=off and co:koRTmp=off and fb:md01=false and fb:kd06=false and (fb:gd05=true or fb:gd07=true) | s mot m |
| kv01 | sw | kv01straight | straight | sw:kv02=straight | sw:kv01=turnout |  |
| kv01 | sw | kv01turnout | turnout | sw:kv02=turnout | sw:kv01=straight |  |
| kv02 | sw | kv02straight | straight | sw:kv01=straight | sw:kv02=turnout |  |
| kv02 | sw | kv02turnout | turnout | sw:kv01=turnout | sw:kv02=straight |  |
| kv04 | sw | kv04straight | straight | sw:kv05=straight | sw:kv04=turnout |  |
| kv04 | sw | kv04turnout | turnout | sw:kv05=turnout | sw:kv04=straight |  |
| kv05 | sw | kv05straight | straight | sw:kv04=straight | sw:kv05=turnout |  |
| kv05 | sw | kv05turnout | turnout | sw:kv04=turnout | sw:kv05=straight |  |

## Mjøndalen (m)

### 1. Turnouts that affect signals

| Signal | Aspect | Turnout | How | Full condition |
|---|---|---|---|---|
| ms02 | green | mv01 | condition straight (required), trigger sg:ms10=green | sw:mv03=straight and sw:mv01=straight |
| ms02 | green | mv03 | condition straight (required), trigger sg:ms10=green | sw:mv03=straight and sw:mv01=straight |
| ms02 | yellow | mv01 | condition straight (required), trigger sg:ms11=green | sw:mv06=straight and sw:mv03=turnout and sw:mv01=straight |
| ms02 | yellow | mv01 | condition turnout (required), trigger sg:ms09=green | sw:mv04=straight and sw:mv01=turnout |
| ms02 | yellow | mv03 | condition turnout (required), trigger sg:ms11=green | sw:mv06=straight and sw:mv03=turnout and sw:mv01=straight |
| ms02 | yellow | mv04 | condition straight (required), trigger sg:ms09=green | sw:mv04=straight and sw:mv01=turnout |
| ms02 | yellow | mv06 | condition straight (required), trigger sg:ms11=green | sw:mv06=straight and sw:mv03=turnout and sw:mv01=straight |
| ms03 | green | mv01 | condition straight (required), trigger co:moINk=on | sw:mv01=straight and sw:mv03=straight and fb:md02=false and fb:md05=false |
| ms03 | green | mv03 | condition straight (required), trigger co:moINk=on | sw:mv01=straight and sw:mv03=straight and fb:md02=false and fb:md05=false |
| ms03 | yellow | mv01 | condition straight (required), trigger co:moINk=on | sw:mv01=straight and sw:mv03=turnout and fb:md04=false |
| ms03 | yellow | mv01 | condition turnout (required), trigger co:moINk=on | sw:mv01=turnout and fb:md03=false |
| ms03 | yellow | mv03 | condition turnout (required), trigger co:moINk=on | sw:mv01=straight and sw:mv03=turnout and fb:md04=false |
| ms06 | green | mv01 | condition turnout (required), trigger co:moUTk=on | sw:mv01=turnout |
| ms07 | green | mv01 | condition straight (required), trigger co:moUTk=on | sw:mv03=straight and sw:mv01=straight |
| ms07 | green | mv03 | condition straight (required), trigger co:moUTk=on | sw:mv03=straight and sw:mv01=straight |
| ms08 | green | mv01 | condition straight (required), trigger co:moUTk=on | sw:mv03=turnout and sw:mv01=straight |
| ms08 | green | mv03 | condition turnout (required), trigger co:moUTk=on | sw:mv03=turnout and sw:mv01=straight |
| ms09 | green | mv08 | condition straight (required), trigger co:moUTy=on | sw:mv08=straight and sw:mv12=turnout and sw:mv14=straight and fb:yd05=false |
| ms09 | green | mv12 | condition turnout (required), trigger co:moUTy=on | sw:mv08=straight and sw:mv12=turnout and sw:mv14=straight and fb:yd05=false |
| ms09 | green | mv14 | condition straight (required), trigger co:moUTy=on | sw:mv08=straight and sw:mv12=turnout and sw:mv14=straight and fb:yd05=false |
| ms10 | green | mv12 | condition straight (required), trigger co:moUTy=on | sw:mv12=straight and sw:mv14=straight and fb:yd05=false |
| ms10 | green | mv14 | condition straight (required), trigger co:moUTy=on | sw:mv12=straight and sw:mv14=straight and fb:yd05=false |
| ms11 | green | mv11 | condition straight (required), trigger co:moUTy=on | sw:mv11=straight and sw:mv14=turnout and fb:yd05=false |
| ms11 | green | mv14 | condition turnout (required), trigger co:moUTy=on | sw:mv11=straight and sw:mv14=turnout and fb:yd05=false |
| ms13 | yellow | mv08 | condition turnout (required), trigger co:moUTy=on | sw:mv08=turnout and sw:mv12=turnout and sw:mv14=straight and fb:yd05=false |
| ms13 | yellow | mv12 | condition turnout (required), trigger co:moUTy=on | sw:mv08=turnout and sw:mv12=turnout and sw:mv14=straight and fb:yd05=false |
| ms13 | yellow | mv14 | condition straight (required), trigger co:moUTy=on | sw:mv08=turnout and sw:mv12=turnout and sw:mv14=straight and fb:yd05=false |
| ms14 | green | mv12 | condition straight (required), trigger co:moINy=on | sw:mv14=straight and sw:mv12=straight and fb:md08=false and fb:md05=false |
| ms14 | green | mv14 | condition straight (required), trigger co:moINy=on | sw:mv14=straight and sw:mv12=straight and fb:md08=false and fb:md05=false |
| ms14 | yellow | mv12 | condition turnout (required), trigger co:moINy=on | sw:mv14=straight and sw:mv12=turnout |
| ms14 | yellow | mv14 | condition straight (required), trigger co:moINy=on | sw:mv14=straight and sw:mv12=turnout |
| ms14 | yellow | mv14 | condition turnout (required), trigger co:moINy=on | sw:mv14=turnout |
| ms15 | green | mv12 | condition straight (required), trigger sg:ms07=green | sw:mv12=straight and sw:mv14=straight |
| ms15 | green | mv14 | condition straight (required), trigger sg:ms07=green | sw:mv12=straight and sw:mv14=straight |
| ms15 | yellow | mv04 | condition straight (required), trigger sg:ms06=green | sw:mv04=straight and sw:mv08=straight and sw:mv12=turnout and sw:mv14=straight |
| ms15 | yellow | mv06 | condition straight (required), trigger sg:ms08=green | sw:mv06=straight and sw:mv11=straight and sw:mv14=turnout |
| ms15 | yellow | mv08 | condition straight (required), trigger sg:ms06=green | sw:mv04=straight and sw:mv08=straight and sw:mv12=turnout and sw:mv14=straight |
| ms15 | yellow | mv11 | condition straight (required), trigger sg:ms08=green | sw:mv06=straight and sw:mv11=straight and sw:mv14=turnout |
| ms15 | yellow | mv12 | condition turnout (required), trigger sg:ms06=green | sw:mv04=straight and sw:mv08=straight and sw:mv12=turnout and sw:mv14=straight |
| ms15 | yellow | mv14 | condition straight (required), trigger sg:ms06=green | sw:mv04=straight and sw:mv08=straight and sw:mv12=turnout and sw:mv14=straight |
| ms15 | yellow | mv14 | condition turnout (required), trigger sg:ms08=green | sw:mv06=straight and sw:mv11=straight and sw:mv14=turnout |

### 2. Sensors that stop signals from showing proceed

Sensor conditions on green/yellow/white actions, and red actions triggered when a sensor goes occupied.

| Signal | Aspect | Sensor | Block | How |
|---|---|---|---|---|
| ms03 | green | md02 |  | must be free; trigger co:moINk=on |
| ms03 | green | md05 |  | must be free; trigger co:moINk=on |
| ms03 | yellow | md03 |  | must be free; trigger co:moINk=on |
| ms03 | yellow | md04 |  | must be free; trigger co:moINk=on |
| ms04 | red | kd06 |  | occupied sets red; condition (sg:ms04=yellow or sg:ms04=green) |
| ms09 | green | yd05 |  | must be free; trigger co:moUTy=on |
| ms10 | green | yd05 |  | must be free; trigger co:moUTy=on |
| ms11 | green | yd05 |  | must be free; trigger co:moUTy=on |
| ms13 | yellow | yd05 |  | must be free; trigger co:moUTy=on |
| ms14 | green | md05 |  | must be free; trigger co:moINy=on |
| ms14 | green | md08 |  | must be free; trigger co:moINy=on |

### 3.1 Signals triggered by other signals

| Signal | Aspect | Triggered by signal | When | Conditions |
|---|---|---|---|---|
| ms01 | green | ms03 | green | - |
| ms01 | red | ms03 | red | - |
| ms01 | yellow | ms03 | yellow | - |
| ms02 | green | ms10 | green | sw:mv03=straight and sw:mv01=straight |
| ms02 | yellow | ms09 | green | sw:mv04=straight and sw:mv01=turnout |
| ms02 | yellow | ms11 | green | sw:mv06=straight and sw:mv03=turnout and sw:mv01=straight |
| ms04 | green | ms07 | green | - |
| ms04 | yellow | ms06 | green | - |
| ms04 | yellow | ms08 | green | - |
| ms13 | green | ms10 | green | - |
| ms13 | yellow | ms09 | green | - |
| ms13 | yellow | ms11 | green | - |
| ms15 | green | ms07 | green | sw:mv12=straight and sw:mv14=straight |
| ms15 | yellow | ms06 | green | sw:mv04=straight and sw:mv08=straight and sw:mv12=turnout and sw:mv14=straight |
| ms15 | yellow | ms08 | green | sw:mv06=straight and sw:mv11=straight and sw:mv14=turnout |
| ms16 | green | ms14 | green | - |
| ms16 | red | ms14 | red | - |
| ms16 | yellow | ms14 | yellow | - |

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| md14 | fb | md14off | off | co:dirRes=on | - |  |
| moINk | co | moINkOff | off | co:moSki=on | - |  |
| moINk | co | moINkOff | off | co:moUTk=on | - |  |
| moINk | co | moINkOff | off | fb:md01=true | co:moINk=on |  |
| moINk | co | moINkOff | off | sw:mv01=any | - |  |
| moINk | co | moINkOn | on | fb:md10=true | co:moSki=off |  |
| moINy | co | moINyOff | off | co:moSki=on | - |  |
| moINy | co | moINyOff | off | co:moUTy=on | - |  |
| moINy | co | moINyOff | off | fb:md08=true | co:moINy=on |  |
| moINy | co | moINyOff | off | sw:mv08=any | sw:mv12=turnout and sw:mv14=straight |  |
| moINy | co | moINyOff | off | sw:mv11=any | sw:mv14=turnout |  |
| moINy | co | moINyOff | off | sw:mv12=any | sw:mv14=straight |  |
| moINy | co | moINyOff | off | sw:mv14=any | - |  |
| moINy | co | moINyOn | on | fb:md11=true | co:moSki=off |  |
| moP1 | co | moP1off | off | co:moP2=off | co:moP1=on |  |
| moP1 | co | moP1off | off | co:moSki=off | - |  |
| moP1 | co | moP1off | off | fb:md08=false | - |  |
| moP1 | co | moP1off | off | sg:ms13=red | sg:ms13=yellow and sg:ms13=green |  |
| moP1 | co | moP1on | on | co:moP2=on | co:moP1=off |  |
| moP1 | co | moP1on | on | co:moSki=on | - |  |
| moP1 | co | moP1on | on | sg:ms13=green | - |  |
| moP1 | co | moP1on | on | sg:ms13=yellow | - |  |
| moP1 | co | moP1on | on | sg:ms14=green | - |  |
| moP1 | co | moP1on | on | sg:ms14=yellow | - |  |
| moP2 | co | moP2off | off | co:moP1=off | co:moP2=on |  |
| moP2 | co | moP2on | on | co:moP1=on | co:moP2=off |  |
| moSki | co | moSkiFlip | flip | fb:md13=any | - |  |
| moUTk | co | moUTkOff | off | co:koRTmp=off | co:moUTk=on |  |
| moUTk | co | moUTkOff | off | co:moINk=on | - |  |
| moUTk | co | moUTkOff | off | co:moSki=on | - |  |
| moUTk | co | moUTkOff | off | fb:kd06=true | co:moUTk=on |  |
| moUTk | co | moUTkOff | off | sw:mv01=any | - |  |
| moUTk | co | moUTkOn | on | fb:md09=true | co:moSki=off and st:krt-gm=unlocked and st:krt-sm=unlocked and st:krt-mg=unlocked and st:krt-ms=unlocked and fb:kd06=false |  |
| moUTy | co | moUTyOff | off | co:moINy=on | - |  |
| moUTy | co | moUTyOff | off | co:moSki=on | - |  |
| moUTy | co | moUTyOff | off | fb:yd05=true | co:moUTy=on |  |
| moUTy | co | moUTyOff | off | sw:mv08=any | sw:mv12=turnout and sw:mv14=straight |  |
| moUTy | co | moUTyOff | off | sw:mv11=any | sw:mv14=turnout |  |
| moUTy | co | moUTyOff | off | sw:mv12=any | sw:mv14=straight |  |
| moUTy | co | moUTyOff | off | sw:mv14=any | - |  |
| moUTy | co | moUTyOn | on | fb:md12=true | co:moSki=off |  |
| mtxDir | tx | mtxDirSkifte | update | fb:md14=true | - |  |
| mtxDir | tx | mtxDirSolberg | update | fb:md14=false | - |  |
| mv01 | sw | mv01straight | straight | sw:mv02=straight | sw:mv01=turnout |  |
| mv01 | sw | mv01turnout | turnout | sw:mv02=turnout | sw:mv01=straight |  |
| mv02 | sw | mv02straight | straight | sw:mv01=straight | sw:mv02=turnout |  |
| mv02 | sw | mv02turnout | turnout | sw:mv01=turnout | sw:mv02=straight |  |
| mv12 | sw | mv12straight | straight | sw:mv13=straight | sw:mv12=turnout |  |
| mv12 | sw | mv12turnout | turnout | sw:mv13=turnout | sw:mv12=straight |  |
| mv13 | sw | mv13straight | straight | sw:mv12=straight | sw:mv13=turnout |  |
| mv13 | sw | mv13turnout | turnout | sw:mv12=turnout | sw:mv13=straight |  |

## Myra (y)

### 1. Turnouts that affect signals

| Signal | Aspect | Turnout | How | Full condition |
|---|---|---|---|---|
| ys01 | green | yv05 | condition turnout (required), trigger co:ys01ctl=on | sw:yv06=straight and sw:yv05=turnout |
| ys01 | green | yv06 | condition straight (required), trigger co:ys01ctl=on | sw:yv06=straight and sw:yv05=turnout |
| ys01 | yellow | yv05 | condition straight (required), trigger co:ys01ctl=on | sw:yv06=straight and sw:yv05=straight |
| ys01 | yellow | yv06 | condition straight (required), trigger co:ys01ctl=on | sw:yv06=straight and sw:yv05=straight |
| ys02 | green | yv06 | condition straight (required), trigger co:ys02ctl=on | sw:yv06=straight and sw:yv09=turnout |
| ys02 | green | yv09 | condition turnout (required), trigger co:ys02ctl=on | sw:yv06=straight and sw:yv09=turnout |
| ys02 | yellow | yv06 | condition turnout (required), trigger co:ys02ctl=on | sw:yv06=turnout |
| ys04 | green | yv02 | condition turnout (required), trigger sg:ks01=red | fb:yd04=true and sw:yv02=turnout and (st:krt-is=locked or st:krt-ig=locked) |
| ys04 | red | yv02 | condition straight (required), trigger fb:nd25=true | sg:ys04=yellow and sw:yv02=straight |
| ys04 | red | yv02 | condition turnout (required), trigger fb:kd07=true | sg:ys04=green and sw:yv02=turnout |
| ys04 | red | yv02 | trigger when straight | (sg:ys04=green or sg:ys04=yellow or st:nrt-in-i1=unlocked) |
| ys04 | red | yv02 | trigger when turnout | (sg:ys04=yellow or sg:ys04=green or st:krt-is=unlocked) |
| ys05 | green | yv03 | condition straight (required), trigger co:ioINy=on | sw:yv03=straight and sw:yv04=straight and sw:yv05=straight and sw:yv06=straight and (sg:ms13=green or sg:ms13=yellow or fb:yd05=true) |
| ys05 | green | yv03 | condition turnout (required), trigger co:ioINy=on | sw:yv03=turnout and sw:yv04=straight and sw:yv05=straight and sw:yv06=straight and (fb:yd01=true or fb:yd05=true) |
| ys05 | green | yv04 | condition straight (required), trigger co:ioINy=on | sw:yv03=straight and sw:yv04=straight and sw:yv05=straight and sw:yv06=straight and (sg:ms13=green or sg:ms13=yellow or fb:yd05=true) |
| ys05 | green | yv04 | condition straight (required), trigger co:ioINy=on | sw:yv03=turnout and sw:yv04=straight and sw:yv05=straight and sw:yv06=straight and (fb:yd01=true or fb:yd05=true) |
| ys05 | green | yv05 | condition straight (required), trigger co:ioINy=on | sw:yv03=straight and sw:yv04=straight and sw:yv05=straight and sw:yv06=straight and (sg:ms13=green or sg:ms13=yellow or fb:yd05=true) |
| ys05 | green | yv05 | condition straight (required), trigger co:ioINy=on | sw:yv03=turnout and sw:yv04=straight and sw:yv05=straight and sw:yv06=straight and (fb:yd01=true or fb:yd05=true) |
| ys05 | green | yv06 | condition straight (required), trigger co:ioINy=on | sw:yv03=straight and sw:yv04=straight and sw:yv05=straight and sw:yv06=straight and (sg:ms13=green or sg:ms13=yellow or fb:yd05=true) |
| ys05 | green | yv06 | condition straight (required), trigger co:ioINy=on | sw:yv03=turnout and sw:yv04=straight and sw:yv05=straight and sw:yv06=straight and (fb:yd01=true or fb:yd05=true) |
| ys05 | red | yv05 | trigger when any | (sg:ys05=yellow or sg:ys05=green) |
| ys05 | yellow | yv03 | condition straight (required), trigger co:ioINy=on | sw:yv03=straight and sw:yv04=straight and sw:yv05=straight and sw:yv06=turnout and (sg:ms13=green or sg:ms13=yellow or fb:yd05=true) |
| ys05 | yellow | yv03 | condition turnout (required), trigger co:ioINy=on | sw:yv03=turnout and sw:yv04=straight and sw:yv05=straight and sw:yv06=turnout and (fb:yd01=true or fb:yd05=true) |
| ys05 | yellow | yv04 | condition straight (required), trigger co:ioINy=on | sw:yv03=straight and sw:yv04=straight and sw:yv05=straight and sw:yv06=turnout and (sg:ms13=green or sg:ms13=yellow or fb:yd05=true) |
| ys05 | yellow | yv04 | condition straight (required), trigger co:ioINy=on | sw:yv03=turnout and sw:yv04=straight and sw:yv05=straight and sw:yv06=turnout and (fb:yd01=true or fb:yd05=true) |
| ys05 | yellow | yv05 | condition straight (required), trigger co:ioINy=on | sw:yv03=straight and sw:yv04=straight and sw:yv05=straight and sw:yv06=turnout and (sg:ms13=green or sg:ms13=yellow or fb:yd05=true) |
| ys05 | yellow | yv05 | condition straight (required), trigger co:ioINy=on | sw:yv03=turnout and sw:yv04=straight and sw:yv05=straight and sw:yv06=turnout and (fb:yd01=true or fb:yd05=true) |
| ys05 | yellow | yv06 | condition turnout (required), trigger co:ioINy=on | sw:yv03=straight and sw:yv04=straight and sw:yv05=straight and sw:yv06=turnout and (sg:ms13=green or sg:ms13=yellow or fb:yd05=true) |
| ys05 | yellow | yv06 | condition turnout (required), trigger co:ioINy=on | sw:yv03=turnout and sw:yv04=straight and sw:yv05=straight and sw:yv06=turnout and (fb:yd01=true or fb:yd05=true) |
| ys06 | green | yv06 | condition straight (required), trigger co:ioINy=on | sw:yv09=straight and sw:yv06=straight and (st:krt-ki=locked or st:nrt-u2-ut=locked or fb:yd03=true) |
| ys06 | green | yv06 | condition straight (required), trigger co:ioINy=on | sw:yv09=turnout and sw:yv06=straight |
| ys06 | green | yv09 | condition straight (required), trigger co:ioINy=on | sw:yv09=straight and sw:yv06=straight and (st:krt-ki=locked or st:nrt-u2-ut=locked or fb:yd03=true) |
| ys06 | green | yv09 | condition turnout (required), trigger co:ioINy=on | sw:yv09=turnout and sw:yv06=straight |
| ys06 | red | yv06 | condition straight (required), trigger fb:yd07=true | sw:yv06=straight |

### 2. Sensors that stop signals from showing proceed

Sensor conditions on green/yellow/white actions, and red actions triggered when a sensor goes occupied.

| Signal | Aspect | Sensor | Block | How |
|---|---|---|---|---|
| ys04 | red | kd07 |  | occupied sets red; condition sg:ys04=green and sw:yv02=turnout |
| ys04 | red | nd25 | nd25 | occupied sets red; condition sg:ys04=yellow and sw:yv02=straight |
| ys05 | red | yd06 |  | occupied sets red; condition (sg:ys05=green or sg:ys05=yellow) |
| ys06 | red | yd07 |  | occupied sets red; condition sw:yv06=straight |
| ys07 | red | yd03 | n-ut | occupied sets red; condition sg:ys07=green |
| ys08 | red | yd03 | n-ut | occupied sets red; condition sg:ys08=green |

### 2.1 Routes that set signals

Rocrail sets these aspects only when it can lock the route, so an occupied destination block stops them.

| Signal | Aspect when set | Route | From -> to block |
|---|---|---|---|
| ys04 | green | krt-ig | i2 -> k1 |
| ys04 | green | krt-is | i2 -> s3 |
| ys04 | yellow | nrt-in-i1 | n-in -> n-i1 |
| ys07 | green | krt-ki | k1 -> n-ut |
| ys08 | green | nrt-u2-ut | n-u2 -> n-ut |

### 3.1 Signals triggered by other signals

| Signal | Aspect | Triggered by signal | When | Conditions |
|---|---|---|---|---|
| ys04 | green | ks01 | red | fb:yd04=true and sw:yv02=turnout and (st:krt-is=locked or st:krt-ig=locked) |

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| yd03d | co | yd3dOff | off | fb:yd03=false | - |  |
| yd03d | co | yd3dOff | off | sw:yv06=any | fb:yd03=false and co:yd03d=on |  |
| yd03d | co | yd3dOn | on | co:yd03d=off | fb:yd03=true |  |
| yd03d | co | yd3dOn | on | fb:yd03=true | - |  |
| yoP1 | co | yoP1off | off | fb:yd05=false | - |  |
| yoP1 | co | yoP1off | off | sw:yv03=turnout | - |  |
| yoP1 | co | yoP1on | on | fb:yd05=true | sw:yv03=straight |  |
| yoP1 | co | yoP1on | on | sw:yv03=straight | fb:yd05=true |  |
| ys01ctl | co | ys01ctlOff | off | co:ioINy=off | - |  |
| ys01ctl | co | ys01ctlOff | off | fb:yd06=true | sw:yv06=straight |  |
| ys01ctl | co | ys01ctlOff | off | sw:yv06=any | - |  |
| ys01ctl | co | ys01ctlOn | on | co:ioUTy=on | fb:yd08=true |  |
| ys01ctl | co | ys01ctlOn | on | sg:is04=green | sw:iv01=straight |  |
| ys01ctl | co | ys01ctlOn | on | sg:is05=green | sw:iv01=straight |  |
| ys01ctl | co | ys01ctlOn | on | sg:is06=green | sw:iv01=straight |  |
| ys01ctl | co | ys01ctlOn | on | sg:is07=green | sw:iv01=straight |  |
| ys02ctl | co | ys02ctlOff | off | co:ioINy=off | - |  |
| ys02ctl | co | ys02ctlOff | off | fb:yd03=true | sw:yv06=straight |  |
| ys02ctl | co | ys02ctlOff | off | fb:yd06=true | sw:yv06=turnout |  |
| ys02ctl | co | ys02ctlOff | off | sw:yv06=any | - |  |
| ys02ctl | co | ys02ctlOn | on | co:ioUTy=on | fb:yd07=true |  |
| ys02ctl | co | ys02ctlOn | on | sg:is04=green | sw:iv01=turnout and sw:yv08=straight |  |
| ys02ctl | co | ys02ctlOn | on | sg:is05=green | sw:iv01=turnout and sw:yv08=straight |  |
| ys02ctl | co | ys02ctlOn | on | sg:is06=green | sw:iv01=turnout and sw:yv08=straight |  |
| ys02ctl | co | ys02ctlOn | on | sg:is07=green | sw:iv01=turnout and sw:yv08=straight |  |
| ys02ctl | co | ys02ctlOn | on | sg:is09=green | sw:iv01=straight and sw:yv08=straight |  |
| yv06 | sw | yv06straight | straight | sw:yv07=straight | sw:yv06=turnout |  |
| yv06 | sw | yv06turnout | turnout | sw:yv07=turnout | sw:yv06=straight |  |
| yv07 | sw | yv07straight | straight | sw:yv06=straight | sw:yv07=turnout |  |
| yv07 | sw | yv07turnout | turnout | sw:yv06=turnout | sw:yv07=straight |  |

## Sigdal (i)

### 1. Turnouts that affect signals

| Signal | Aspect | Turnout | How | Full condition |
|---|---|---|---|---|
| is01 | green | iv01 | condition straight (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=turnout and sw:yv08=straight and sw:iv01=straight |
| is01 | green | iv01 | condition straight (required), trigger co:ioINy=on | fb:yd07=true and sw:yv08=straight and sw:iv01=straight |
| is01 | green | iv01 | condition straight (required), trigger sg:ys05=yellow | sw:iv01=straight |
| is01 | green | iv01 | condition straight (required), trigger sg:ys06=green | sw:yv07=straight and sw:iv01=straight |
| is01 | green | yv04 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=turnout and sw:yv08=straight and sw:iv01=straight |
| is01 | green | yv06 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=turnout and sw:yv08=straight and sw:iv01=straight |
| is01 | green | yv07 | condition straight (required), trigger sg:ys06=green | sw:yv07=straight and sw:iv01=straight |
| is01 | green | yv08 | condition straight (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=turnout and sw:yv08=straight and sw:iv01=straight |
| is01 | green | yv08 | condition straight (required), trigger co:ioINy=on | fb:yd07=true and sw:yv08=straight and sw:iv01=straight |
| is01 | red | iv01 | condition straight (required), trigger fb:id02=true | sw:iv01=straight and sg:is01=green |
| is01 | red | yv06 | trigger when any | - |
| is01 | yellow | iv01 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=turnout and sw:yv08=straight and sw:iv01=turnout |
| is01 | yellow | iv01 | condition turnout (required), trigger co:ioINy=on | fb:yd07=true and sw:yv08=straight and sw:iv01=turnout |
| is01 | yellow | iv01 | condition turnout (required), trigger sg:ys05=yellow | sw:iv01=turnout |
| is01 | yellow | iv01 | condition turnout (required), trigger sg:ys06=green | sw:yv07=straight and sw:iv01=turnout |
| is01 | yellow | yv04 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=turnout and sw:yv08=straight and sw:iv01=turnout |
| is01 | yellow | yv06 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=turnout and sw:yv08=straight and sw:iv01=turnout |
| is01 | yellow | yv07 | condition straight (required), trigger sg:ys06=green | sw:yv07=straight and sw:iv01=turnout |
| is01 | yellow | yv08 | condition straight (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=turnout and sw:yv08=straight and sw:iv01=turnout |
| is01 | yellow | yv08 | condition straight (required), trigger co:ioINy=on | fb:yd07=true and sw:yv08=straight and sw:iv01=turnout |
| is02 | green | iv01 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=straight and sw:iv12=straight and sw:iv13=straight |
| is02 | green | iv04 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=straight and sw:iv12=straight and sw:iv13=straight |
| is02 | green | iv06 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=straight and sw:iv12=straight and sw:iv13=straight |
| is02 | green | iv12 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=straight and sw:iv12=straight and sw:iv13=straight |
| is02 | green | iv13 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=straight and sw:iv12=straight and sw:iv13=straight |
| is02 | red | yv06 | trigger when any | - |
| is02 | yellow | iv01 | condition straight (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv01 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv01 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=turnout and sw:iv16=straight and sw:iv11=straight and sw:iv13=turnout |
| is02 | yellow | iv01 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=turnout and sw:iv12=turnout and sw:iv13=straight |
| is02 | yellow | iv04 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv04 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=turnout and sw:iv16=straight and sw:iv11=straight and sw:iv13=turnout |
| is02 | yellow | iv04 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=turnout and sw:iv12=turnout and sw:iv13=straight |
| is02 | yellow | iv05 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv05 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=turnout and sw:iv16=straight and sw:iv11=straight and sw:iv13=turnout |
| is02 | yellow | iv06 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=turnout and sw:iv12=turnout and sw:iv13=straight |
| is02 | yellow | iv07 | condition straight (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv08 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv08 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv09 | condition straight (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv09 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv10 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv10 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv11 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=turnout and sw:iv16=straight and sw:iv11=straight and sw:iv13=turnout |
| is02 | yellow | iv11 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv11 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv12 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=turnout and sw:iv12=turnout and sw:iv13=straight |
| is02 | yellow | iv13 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=turnout and sw:iv06=turnout and sw:iv12=turnout and sw:iv13=straight |
| is02 | yellow | iv13 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv13 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv13 | condition turnout (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=turnout and sw:iv16=straight and sw:iv11=straight and sw:iv13=turnout |
| is02 | yellow | iv14 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv15 | condition straight (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv16 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=turnout and sw:iv16=straight and sw:iv11=straight and sw:iv13=turnout |
| is02 | yellow | iv17 | condition straight (required), trigger co:ioUTs=on | sw:iv01=straight and sw:iv15=straight and sw:iv07=straight and sw:iv08=turnout and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is02 | yellow | iv17 | condition straight (required), trigger co:ioUTs=on | sw:iv01=turnout and sw:iv04=straight and sw:iv05=straight and sw:iv14=straight and sw:iv08=straight and sw:iv17=straight and sw:iv09=straight and sw:iv10=turnout and sw:iv11=turnout and sw:iv13=turnout |
| is03 | green | iv01 | condition straight (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | iv01 | condition straight (required), trigger co:ioINy=on | fb:yd08=true and sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | iv01 | condition straight (required), trigger sg:ys05=green | sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | iv04 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | iv04 | condition turnout (required), trigger co:ioINy=on | fb:yd08=true and sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | iv04 | condition turnout (required), trigger sg:ys05=green | sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | iv06 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | iv06 | condition turnout (required), trigger co:ioINy=on | fb:yd08=true and sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | iv06 | condition turnout (required), trigger sg:ys05=green | sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | yv04 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | green | yv06 | condition straight (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | red | yv06 | trigger when any | - |
| is03 | yellow | iv01 | condition straight (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | iv01 | condition straight (required), trigger co:ioINy=on | fb:yd08=true and sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | iv01 | condition straight (required), trigger sg:ys05=green | sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | iv04 | condition straight (one of (or)), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | iv04 | condition straight (one of (or)), trigger co:ioINy=on | fb:yd08=true and sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | iv04 | condition straight (one of (or)), trigger sg:ys05=green | sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | iv06 | condition straight (one of (or)), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | iv06 | condition straight (one of (or)), trigger co:ioINy=on | fb:yd08=true and sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | iv06 | condition straight (one of (or)), trigger sg:ys05=green | sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | yv04 | condition turnout (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is03 | yellow | yv06 | condition straight (required), trigger co:ioINy=on | fb:yd02=true and sw:yv04=turnout and sw:yv06=straight and sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |
| is04 | green | iv01 | condition straight (required), trigger co:ioUTy=on | fb:id06=true and sw:iv06=turnout and sw:iv04=turnout and sw:iv01=straight |
| is04 | green | iv01 | condition turnout (required), trigger co:ioUTy=on | fb:id06=true and sw:iv06=turnout and sw:iv04=turnout and sw:iv01=turnout and sw:yv08=straight |
| is04 | green | iv04 | condition turnout (required), trigger co:ioUTy=on | fb:id06=true and sw:iv06=turnout and sw:iv04=turnout and sw:iv01=straight |
| is04 | green | iv04 | condition turnout (required), trigger co:ioUTy=on | fb:id06=true and sw:iv06=turnout and sw:iv04=turnout and sw:iv01=turnout and sw:yv08=straight |
| is04 | green | iv06 | condition turnout (required), trigger co:ioUTy=on | fb:id06=true and sw:iv06=turnout and sw:iv04=turnout and sw:iv01=straight |
| is04 | green | iv06 | condition turnout (required), trigger co:ioUTy=on | fb:id06=true and sw:iv06=turnout and sw:iv04=turnout and sw:iv01=turnout and sw:yv08=straight |
| is04 | green | yv08 | condition straight (required), trigger co:ioUTy=on | fb:id06=true and sw:iv06=turnout and sw:iv04=turnout and sw:iv01=turnout and sw:yv08=straight |
| is05 | green | iv01 | condition straight (required), trigger co:ioUTy=on | fb:id05=true and sw:iv06=straight and sw:iv04=turnout and sw:iv01=straight |
| is05 | green | iv01 | condition turnout (required), trigger co:ioUTy=on | fb:id05=true and sw:iv06=straight and sw:iv04=turnout and sw:iv01=turnout and sw:yv08=straight |
| is05 | green | iv04 | condition turnout (required), trigger co:ioUTy=on | fb:id05=true and sw:iv06=straight and sw:iv04=turnout and sw:iv01=straight |
| is05 | green | iv04 | condition turnout (required), trigger co:ioUTy=on | fb:id05=true and sw:iv06=straight and sw:iv04=turnout and sw:iv01=turnout and sw:yv08=straight |
| is05 | green | iv06 | condition straight (required), trigger co:ioUTy=on | fb:id05=true and sw:iv06=straight and sw:iv04=turnout and sw:iv01=straight |
| is05 | green | iv06 | condition straight (required), trigger co:ioUTy=on | fb:id05=true and sw:iv06=straight and sw:iv04=turnout and sw:iv01=turnout and sw:yv08=straight |
| is05 | green | yv08 | condition straight (required), trigger co:ioUTy=on | fb:id05=true and sw:iv06=straight and sw:iv04=turnout and sw:iv01=turnout and sw:yv08=straight |
| is06 | green | iv01 | condition straight (required), trigger co:ioUTy=on | fb:id04=true and sw:iv05=turnout and sw:iv04=straight and sw:iv01=straight |
| is06 | green | iv01 | condition turnout (required), trigger co:ioUTy=on | fb:id04=true and sw:iv05=turnout and sw:iv04=straight and sw:iv01=turnout and sw:yv08=straight |
| is06 | green | iv04 | condition straight (required), trigger co:ioUTy=on | fb:id04=true and sw:iv05=turnout and sw:iv04=straight and sw:iv01=straight |
| is06 | green | iv04 | condition straight (required), trigger co:ioUTy=on | fb:id04=true and sw:iv05=turnout and sw:iv04=straight and sw:iv01=turnout and sw:yv08=straight |
| is06 | green | iv05 | condition turnout (required), trigger co:ioUTy=on | fb:id04=true and sw:iv05=turnout and sw:iv04=straight and sw:iv01=straight |
| is06 | green | iv05 | condition turnout (required), trigger co:ioUTy=on | fb:id04=true and sw:iv05=turnout and sw:iv04=straight and sw:iv01=turnout and sw:yv08=straight |
| is06 | green | yv08 | condition straight (required), trigger co:ioUTy=on | fb:id04=true and sw:iv05=turnout and sw:iv04=straight and sw:iv01=turnout and sw:yv08=straight |
| is07 | green | iv01 | condition straight (required), trigger co:ioUTy=on | fb:id03=true and sw:iv05=straight and sw:iv04=straight and sw:iv01=straight |
| is07 | green | iv01 | condition turnout (required), trigger co:ioUTy=on | fb:id03=true and sw:iv05=straight and sw:iv04=straight and sw:iv01=turnout and sw:yv08=straight |
| is07 | green | iv04 | condition straight (required), trigger co:ioUTy=on | fb:id03=true and sw:iv05=straight and sw:iv04=straight and sw:iv01=straight |
| is07 | green | iv04 | condition straight (required), trigger co:ioUTy=on | fb:id03=true and sw:iv05=straight and sw:iv04=straight and sw:iv01=turnout and sw:yv08=straight |
| is07 | green | iv05 | condition straight (required), trigger co:ioUTy=on | fb:id03=true and sw:iv05=straight and sw:iv04=straight and sw:iv01=straight |
| is07 | green | iv05 | condition straight (required), trigger co:ioUTy=on | fb:id03=true and sw:iv05=straight and sw:iv04=straight and sw:iv01=turnout and sw:yv08=straight |
| is07 | green | yv08 | condition straight (required), trigger co:ioUTy=on | fb:id03=true and sw:iv05=straight and sw:iv04=straight and sw:iv01=turnout and sw:yv08=straight |
| is09 | green | iv02 | condition straight (required), trigger co:ioUTy=on | fb:id02=true and sw:iv02=straight and sw:yv08=straight |
| is09 | green | yv08 | condition straight (required), trigger co:ioUTy=on | fb:id02=true and sw:iv02=straight and sw:yv08=straight |
| is10 | green | iv07 | condition straight (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=turnout and sw:iv07=straight and sw:iv15=straight |
| is10 | green | iv08 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=turnout and sw:iv07=straight and sw:iv15=straight |
| is10 | green | iv09 | condition straight (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=turnout and sw:iv07=straight and sw:iv15=straight |
| is10 | green | iv10 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=turnout and sw:iv07=straight and sw:iv15=straight |
| is10 | green | iv11 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=turnout and sw:iv07=straight and sw:iv15=straight |
| is10 | green | iv13 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=turnout and sw:iv07=straight and sw:iv15=straight |
| is10 | green | iv15 | condition straight (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=turnout and sw:iv07=straight and sw:iv15=straight |
| is10 | green | iv17 | condition straight (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=turnout and sw:iv07=straight and sw:iv15=straight |
| is12 | green | iv08 | condition straight (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=straight |
| is12 | green | iv09 | condition straight (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=straight |
| is12 | green | iv10 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=straight |
| is12 | green | iv11 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=straight |
| is12 | green | iv13 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=straight |
| is12 | green | iv17 | condition straight (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=turnout and sw:iv10=turnout and sw:iv09=straight and sw:iv17=straight and sw:iv08=straight |
| is14 | green | iv12 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=straight and sw:iv12=turnout |
| is14 | green | iv13 | condition straight (required), trigger co:ioUTs=on | sw:iv13=straight and sw:iv12=turnout |
| is15 | green | iv12 | condition straight (required), trigger co:ioUTs=on | sw:iv13=straight and sw:iv12=straight |
| is15 | green | iv13 | condition straight (required), trigger co:ioUTs=on | sw:iv13=straight and sw:iv12=straight |
| is16 | green | iv11 | condition straight (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=straight |
| is16 | green | iv13 | condition turnout (required), trigger co:ioUTs=on | sw:iv13=turnout and sw:iv11=straight |

### 2. Sensors that stop signals from showing proceed

Sensor conditions on green/yellow/white actions, and red actions triggered when a sensor goes occupied.

| Signal | Aspect | Sensor | Block | How |
|---|---|---|---|---|
| is01 | red | id01 |  | occupied sets red; condition sg:is01=yellow |
| is01 | red | id02 |  | occupied sets red; condition sw:iv01=straight and sg:is01=green |
| is03 | red | id01 |  | occupied sets red; condition (sg:is03=green or sg:is03=yellow) |
| is04 | red | id01 |  | occupied sets red; condition (sg:is04=green) |
| is05 | red | id01 |  | occupied sets red; condition (sg:is05=green) |
| is06 | red | id01 |  | occupied sets red; condition (sg:is06=green) |
| is07 | red | id01 |  | occupied sets red; condition (sg:is07=green) |
| is09 | red | yd07 |  | occupied sets red; condition - |
| is12 | red | id08 |  | occupied sets red; condition - |
| is14 | red | id12 | id12 | occupied sets red; condition - |
| is18 | red | id11 |  | occupied sets red; condition - |

### 2.1 Routes that set signals

Rocrail sets these aspects only when it can lock the route, so an occupied destination block stops them.

| Signal | Aspect when set | Route | From -> to block |
|---|---|---|---|
| is17 | green | irt-11-22 | i10 -> i11 |
| is18 | green | irt-22-11 | i11 -> i10 |

### 3.1 Signals triggered by other signals

| Signal | Aspect | Triggered by signal | When | Conditions |
|---|---|---|---|---|
| is01 | green | ys05 | yellow | sw:iv01=straight |
| is01 | green | ys06 | green | sw:yv07=straight and sw:iv01=straight |
| is01 | yellow | ys05 | yellow | sw:iv01=turnout |
| is01 | yellow | ys06 | green | sw:yv07=straight and sw:iv01=turnout |
| is03 | green | ys05 | green | sw:iv01=straight and sw:iv04=turnout and sw:iv06=turnout |
| is03 | yellow | ys05 | green | sw:iv01=straight and (sw:iv04=straight or sw:iv06=straight) |

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| ib11 | co | ib11Off | off | co:rtb-tox=off | - |  |
| ib12 | co | ib12Off | off | co:rtb-tox=off | - |  |
| ib13 | co | ib13Off | off | co:rtb-tox=off | - |  |
| ib14 | co | ib14Off | off | co:rtb-tox=off | - |  |
| ib15 | co | ib15Off | off | co:rtb-tox=off | - |  |
| ib16 | co | ib16Off | off | co:rtb-tox=off | - |  |
| ib17 | co | ib17Off | off | co:rtb-tox=off | - |  |
| ib18 | co | ib18Off | off | co:rtb-tox=off | - |  |
| ib19 | co | ib19Off | off | co:rtb-tox=off | - |  |
| ib20 | co | ib20Off | off | co:rtb-tox=off | - |  |
| ib21 | co | ib21Off | off | co:rtb-tox=off | - |  |
| ib22 | co | ib22Off | off | co:rtb-tox=off | - |  |
| id20 | fb | id20off | off | co:dirRes=on | - |  |
| id20 | fb | id20off | off | fb:id21=true | - |  |
| id21 | fb | id21off | off | co:dirRes=on | - |  |
| id21 | fb | id21off | off | fb:id20=true | - |  |
| ioINs | co | ioINsOff | off | co:ioUTs=on | - |  |
| ioINs | co | ioINsOff | off | fb:id09=true | - |  |
| ioINs | co | ioINsOff | off | sw:iv13=any | - |  |
| ioINs | co | ioINsOn | on | fb:id18=true | - |  |
| ioINs | ext | reset-all | DMJK-reset-all.txt | co:ResetAll=on | - |  |
| ioINy | co | ioINyOff | off | co:ioUTy=on | co:ioINy=on |  |
| ioINy | co | ioINyOff | off | sw:iv01=any | - |  |
| ioINy | co | ioINyOn | on | fb:id17=true | - |  |
| ioUTs | co | ioUTsOff | off | co:ioINs=on | co:ioUTs=on |  |
| ioUTs | co | ioUTsOff | off | fb:id09=true | - |  |
| ioUTs | co | ioUTsOff | off | sw:iv13=any | - |  |
| ioUTs | co | ioUTsOn | on | fb:id19=true | - |  |
| ioUTy | co | ioUTyOff | off | co:ioINy=on | - |  |
| ioUTy | co | ioUTyOff | off | fb:yd06=true | - |  |
| ioUTy | co | ioUTyOff | off | sw:iv01=any | - |  |
| ioUTy | co | ioUTyOff | off | sw:yv05=any | - |  |
| ioUTy | co | ioUTyOff | off | sw:yv06=any | - |  |
| ioUTy | co | ioUTyOn | on | fb:id16=true | - |  |
| irt-11-22 | st | irt-11-22Free | unlock | co:ib11=on | co:ib22=off and st:irt-11-22=locked |  |
| irt-11-22 | st | irt-11-22Free | unlock | fb:id07=true | st:irt-11-22=locked |  |
| irt-11-22 | st | irt-11-22Set | lockset | co:ib22=on | co:ib11=on and st:irt-11-22=unlocked and st:irt-22-11=unlocked |  |
| irt-22-11 | st | irt-22-11Free | unlock | co:ib11=on | co:ib22=off and st:irt-22-11=locked |  |
| irt-22-11 | st | irt-22-11Free | unlock | fb:id11=true | st:irt-22-11=locked |  |
| irt-22-11 | st | irt-22-11Set | lockset | co:ib11=on | co:ib22=on and st:irt-11-22=unlocked and st:irt-22-11=unlocked |  |
| itxDir | tx | itxDirNorb | update | fb:id21=true | fb:id20=false |  |
| itxDir | tx | itxDirSkifte | update | fb:id20=true | fb:id21=false |  |
| itxDir | tx | itxDirSolberg | update | fb:id20=false | fb:id21=false |  |
| itxDir | tx | itxDirSolberg | update | fb:id21=false | fb:id20=false |  |
| iv01 | sw | iv01straight | straight | sw:iv02=straight | sw:iv01=turnout |  |
| iv01 | sw | iv01turnout | turnout | sw:iv02=turnout | sw:iv01=straight |  |
| iv02 | sw | iv02straight | straight | sw:iv01=straight | sw:iv02=turnout |  |
| iv02 | sw | iv02turnout | turnout | sw:iv01=turnout | sw:iv02=straight |  |
| iv07 | sw | iv07turnout | turnout | sw:iv07=straight | sw:iv14=turnout |  |
| iv07 | sw | iv07turnout | turnout | sw:iv15=turnout | sw:iv07=straight |  |
| iv14 | sw | iv14straight | straight | sw:iv15=straight | sw:iv14=turnout |  |
| iv14 | sw | iv14turnout | turnout | sw:iv15=turnout | sw:iv14=straight |  |
| iv15 | sw | iv15straight | straight | sw:iv14=straight | sw:iv15=turnout |  |
| iv15 | sw | iv15turnout | turnout | sw:iv14=turnout | sw:iv15=straight |  |
| iv16 | sw | iv16straight | straight | sw:iv17=straight | sw:iv16=turnout |  |
| iv16 | sw | iv16turnout | turnout | sw:iv17=turnout | sw:iv16=straight |  |
| iv17 | sw | iv17straight | straight | sw:iv16=straight | sw:iv17=turnout |  |
| iv17 | sw | iv17turnout | turnout | sw:iv16=turnout | sw:iv17=straight |  |
| iv18 | sw | iv18straight | straight | sw:iv20=any | (co:ib20=on or co:ib21=on) |  |
| iv19 | sw | iv19straight | straight | sw:iv18=straight | co:ib20=on |  |
| iv19 | sw | iv19turnout | turnout | sw:iv18=straight | co:ib21=on |  |
| iv20 | sw | iv20straight | straight | co:ib11=on | st:irt-11-22=unlocked and (co:ib20=on or co:ib21=on) |  |
| iv20 | sw | iv20straight | straight | co:ib20=on | st:irt-11-22=unlocked and co:ib11=on |  |
| iv20 | sw | iv20straight | straight | co:ib21=on | st:irt-11-22=unlocked and co:ib11=on |  |
| iv20 | sw | iv20turnout | turnout | sw:iv21=turnout | (co:ib20=on or co:ib21=on) |  |
| iv21 | sw | iv21straight | straight | sw:iv23=turnout | co:ib19=on |  |
| iv21 | sw | iv21turnout | turnout | sw:iv23=turnout | (co:ib20=on or co:ib21=on) |  |
| iv22 | sw | iv22straight | straight | co:ib17=on | co:ib18=on |  |
| iv22 | sw | iv22straight | straight | co:ib18=on | co:ib17=on |  |
| iv22 | sw | iv22turnout | turnout | co:ib17=on | co:ib19=on |  |
| iv22 | sw | iv22turnout | turnout | co:ib19=on | co:ib17=on |  |
| iv23 | sw | iv23straight | straight | sw:iv24=turnout | co:ib18=on |  |
| iv23 | sw | iv23turnout | turnout | sw:iv24=turnout | (co:ib19=on or co:ib20=on or co:ib21=on) |  |
| iv24 | sw | iv24straight | straight | sw:iv25=any | (co:ib14=on or co:ib15=on or co:ib16=on) |  |
| iv24 | sw | iv24turnout | turnout | sw:iv25=any | (co:ib18=on or co:ib19=on or co:ib20=on or co:ib21=on) |  |
| iv25 | sw | iv25straight | straight | co:ib13=on | (co:ib14=on or co:ib15=on or co:ib16=on or co:ib18=on or co:ib19=on) |  |
| iv25 | sw | iv25straight | straight | co:ib13=on | st:irt-11-22=unlocked and (co:ib20=on or co:ib21=on) |  |
| iv25 | sw | iv25straight | straight | co:ib14=on | co:ib13=on |  |
| iv25 | sw | iv25straight | straight | co:ib15=on | co:ib13=on |  |
| iv25 | sw | iv25straight | straight | co:ib16=on | co:ib13=on |  |
| iv25 | sw | iv25straight | straight | co:ib18=on | co:ib13=on |  |
| iv25 | sw | iv25straight | straight | co:ib19=on | co:ib13=on |  |
| iv25 | sw | iv25straight | straight | co:ib20=on | st:irt-11-22=unlocked and co:ib13=on |  |
| iv25 | sw | iv25straight | straight | co:ib21=on | st:irt-11-22=unlocked and co:ib13=on |  |
| iv25 | sw | iv25turnout | turnout | co:ib12=on | (co:ib14=on or co:ib15=on or co:ib16=on or co:ib18=on or co:ib19=on) |  |
| iv25 | sw | iv25turnout | turnout | co:ib12=on | st:irt-11-22=unlocked and (co:ib20=on or co:ib21=on) |  |
| iv25 | sw | iv25turnout | turnout | co:ib14=on | co:ib12=on |  |
| iv25 | sw | iv25turnout | turnout | co:ib15=on | co:ib12=on |  |
| iv25 | sw | iv25turnout | turnout | co:ib16=on | co:ib12=on |  |
| iv25 | sw | iv25turnout | turnout | co:ib18=on | co:ib12=on |  |
| iv25 | sw | iv25turnout | turnout | co:ib19=on | co:ib12=on |  |
| iv25 | sw | iv25turnout | turnout | co:ib20=on | st:irt-11-22=unlocked and co:ib12=on |  |
| iv25 | sw | iv25turnout | turnout | co:ib21=on | st:irt-11-22=unlocked and co:ib12=on |  |
| iv26 | sw | iv26straight | straight | sw:iv24=straight | (co:ib15=on or co:ib16=on) |  |
| iv26 | sw | iv26turnout | turnout | sw:iv24=straight | co:ib14=on |  |
| iv27 | sw | iv27straight | straight | sw:iv26=straight | co:ib16=on |  |
| iv27 | sw | iv27turnout | turnout | sw:iv26=straight | co:ib15=on |  |

## Norbotten (n)

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| nb-i1 | co | nb-i1Off | off | co:nb-in=on | co:nb-i1=on |  |
| nb-i1 | co | nb-i1Off | off | co:rtb-tox=off | (co:nb-in=off or st:nrt-in-i1=locked) |  |
| nb-in | co | nb-inOff | off | co:rtb-tox=off | (co:nb-i1=off or st:nrt-in-i1=locked) |  |
| nb-n0 | co | nb-n0Off | off | co:rtb-tox=off | - |  |
| nb-n1 | co | nb-n1Off | off | co:rtb-tox=off | - |  |
| nb-n2 | co | nb-n2Off | off | co:rtb-tox=off | - |  |
| nb-n3 | co | nb-n3Off | off | co:rtb-tox=off | - |  |
| nb-n4 | co | nb-n4Off | off | co:rtb-tox=off | - |  |
| nb-n5 | co | nb-n5Off | off | co:rtb-tox=off | - |  |
| nb-n6 | co | nb-n6Off | off | co:rtb-tox=off | - |  |
| nb-n7 | co | nb-n7Off | off | co:rtb-tox=off | - |  |
| nb-u2 | co | nb-u2Off | off | co:rtb-tox=off | co:nb-ut=off |  |
| nb-ut | co | nb-utOff | off | co:nb-ut=on | co:nb-u2=off |  |
| nb-ut | co | nb-utOff | off | co:rtb-tox=off | co:nb-u2=off |  |
| noRTip | co | noRTipOff | off | co:krt-ki-helper=off | - |  |
| noRTip | co | noRTipOff | off | co:nb-in=on | - |  |
| noRTip | co | noRTipOff | off | fb:id16=true | - |  |
| noRTip | co | noRTipOff | off | fb:yd04=true | co:noRTip=on |  |
| noRTip | co | noRTipOn | on | co:nb-i1=on | co:nb-in=on and st:krt-ig=unlocked and st:krt-is=unlocked and st:krt-ki=locked |  |
| noRTip | co | noRTipOn | on | fb:id16=true | fb:id21=true and sw:iv01=straight and sw:yv05=turnout and st:krt-ig=unlocked and st:krt-is=unlocked and st:nrt-in-i1=unlocked |  |
| noRTup | co | noRTupOff | off | co:krt-ki-helper=off | - |  |
| noRTup | co | noRTupOff | off | co:nb-u2=on | - |  |
| noRTup | co | noRTupOn | on | co:nb-ut=on | co:nb-u2=on and st:krt-ki=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | co:nb-i1=on | st:nrt-i1-i2=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | fb:nd09=true | st:nrt-i2-n1=locked and st:nrt-i1-i2=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | fb:nd10=true | st:nrt-i2-n2=locked and st:nrt-i1-i2=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | fb:nd11=true | st:nrt-i2-n3=locked and st:nrt-i1-i2=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | fb:nd12=true | st:nrt-i2-n4=locked and st:nrt-i1-i2=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | fb:nd13=true | st:nrt-i2-n5=locked and st:nrt-i1-i2=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | fb:nd14=true | st:nrt-i2-n6=locked and st:nrt-i1-i2=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | fb:nd15=true | st:nrt-i2-n7=locked and st:nrt-i1-i2=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Free | unlock | fb:nd24=off | st:nrt-i1-i2=locked and st:nrt-i2-u1=locked |  |
| nrt-i1-i2 | st | nrt-i1-i2Set | lockset | co:nb-n1=on | co:nb-i1=on |  |
| nrt-i1-i2 | st | nrt-i1-i2Set | lockset | co:nb-n2=on | co:nb-i1=on |  |
| nrt-i1-i2 | st | nrt-i1-i2Set | lockset | co:nb-n3=on | co:nb-i1=on |  |
| nrt-i1-i2 | st | nrt-i1-i2Set | lockset | co:nb-n4=on | co:nb-i1=on |  |
| nrt-i1-i2 | st | nrt-i1-i2Set | lockset | co:nb-n5=on | co:nb-i1=on |  |
| nrt-i1-i2 | st | nrt-i1-i2Set | lockset | co:nb-n6=on | co:nb-i1=on |  |
| nrt-i1-i2 | st | nrt-i1-i2Set | lockset | co:nb-n7=on | co:nb-i1=on |  |
| nrt-i1-i2 | st | nrt-i1-i2Set | lockset | co:nb-u2=on | co:nb-i1=on |  |
| nrt-i2-n1 | st | nrt-i2-n1Free | unlock | co:nb-i1=on | st:nrt-i2-n1=locked |  |
| nrt-i2-n1 | st | nrt-i2-n1Free | unlock | fb:nd09=true | st:nrt-i2-n1=locked |  |
| nrt-i2-n1 | st | nrt-i2-n1Set | lockset | co:nb-n1=on | co:nb-i1=on |  |
| nrt-i2-n2 | st | nrt-i2-n2Free | unlock | co:nb-i1=on | st:nrt-i2-n2=locked |  |
| nrt-i2-n2 | st | nrt-i2-n2Free | unlock | fb:nd10=true | st:nrt-i2-n2=locked |  |
| nrt-i2-n2 | st | nrt-i2-n2Set | lockset | co:nb-n2=on | co:nb-i1=on |  |
| nrt-i2-n3 | st | nrt-i2-n3Free | unlock | co:nb-i1=on | st:nrt-i2-n3=locked |  |
| nrt-i2-n3 | st | nrt-i2-n3Free | unlock | fb:nd11=true | st:nrt-i2-n3=locked |  |
| nrt-i2-n3 | st | nrt-i2-n3Set | lockset | co:nb-n3=on | co:nb-i1=on |  |
| nrt-i2-n4 | st | nrt-i2-n4Free | unlock | co:nb-i1=on | st:nrt-i2-n4=locked |  |
| nrt-i2-n4 | st | nrt-i2-n4Free | unlock | fb:nd12=true | st:nrt-i2-n4=locked |  |
| nrt-i2-n4 | st | nrt-i2-n4Set | lockset | co:nb-n4=on | co:nb-i1=on |  |
| nrt-i2-n5 | st | nrt-i2-n5Free | unlock | co:nb-i1=on | st:nrt-i2-n5=locked |  |
| nrt-i2-n5 | st | nrt-i2-n5Free | unlock | fb:nd13=true | st:nrt-i2-n5=locked |  |
| nrt-i2-n5 | st | nrt-i2-n5Set | lockset | co:nb-n5=on | co:nb-i1=on |  |
| nrt-i2-n6 | st | nrt-i2-n6Free | unlock | co:nb-i1=on | st:nrt-i2-n6=locked |  |
| nrt-i2-n6 | st | nrt-i2-n6Free | unlock | fb:nd14=true | st:nrt-i2-n6=locked |  |
| nrt-i2-n6 | st | nrt-i2-n6Set | lockset | co:nb-n6=on | co:nb-i1=on |  |
| nrt-i2-n7 | st | nrt-i2-n7Free | unlock | co:nb-i1=on | st:nrt-i2-n7=locked |  |
| nrt-i2-n7 | st | nrt-i2-n7Free | unlock | fb:nd15=true | st:nrt-i2-n7=locked |  |
| nrt-i2-n7 | st | nrt-i2-n7Set | lockset | co:nb-n7=on | co:nb-i1=on |  |
| nrt-i2-u1 | st | nrt-i2-u1Free | unlock | co:nb-i1=on | st:nrt-i2-u1=locked |  |
| nrt-i2-u1 | st | nrt-i2-u1Free | unlock | fb:nd24=off | st:nrt-i2-u1=locked |  |
| nrt-i2-u1 | st | nrt-i2-u1Set | lockset | co:nb-u2=on | co:nb-i1=on |  |
| nrt-in-i1 | st | nrt-in-i1Free | unlock | co:nb-in=on | st:nrt-in-i1=locked |  |
| nrt-in-i1 | st | nrt-in-i1Free | unlock | fb:nd20=true | st:nrt-in-i1=locked |  |
| nrt-in-i1 | st | nrt-in-i1Set | lockset | co:krt-ki-helper=off | co:noRTip=on |  |
| nrt-in-i1 | st | nrt-in-i1Set | lockset | co:nb-i1=on | co:nb-in=on and st:krt-ig=unlocked and st:krt-is=unlocked and st:krt-ki=unlocked |  |
| nrt-in-i1 | st | nrt-in-i1Set | lockset | fb:id16=true | fb:id21=true and sw:iv01=straight and sw:yv05=turnout and fb:yd04=true and st:krt-ig=unlocked and st:krt-is=unlocked and st:krt-ki=unlocked |  |
| nrt-in-i1 | st | nrt-in-i1Set | lockset | fb:yd04=true | co:noRTip=on and st:krt-ki=unlocked and st:krt-ig=unlocked and st:krt-is=unlocked |  |
| nrt-n0-u1 | st | nrt-n0-u1Free | unlock | co:nb-n0=on | st:nrt-n0-u1=locked |  |
| nrt-n0-u1 | st | nrt-n0-u1Free | unlock | fb:nd24=off | st:nrt-n0-u1=locked |  |
| nrt-n0-u1 | st | nrt-n0-u1Set | lockset | co:nb-u2=on | co:nb-n0=on |  |
| nrt-n1-u1 | st | nrt-n1-u1Free | unlock | co:nb-n1=on | st:nrt-n1-u1=locked |  |
| nrt-n1-u1 | st | nrt-n1-u1Free | unlock | fb:nd24=off | st:nrt-n1-u1=locked |  |
| nrt-n1-u1 | st | nrt-n1-u1Set | lockset | co:nb-u2=on | co:nb-n1=on |  |
| nrt-n2-u1 | st | nrt-n2-u1Free | unlock | co:nb-n2=on | st:nrt-n2-u1=locked |  |
| nrt-n2-u1 | st | nrt-n2-u1Free | unlock | fb:nd24=off | st:nrt-n2-u1=locked |  |
| nrt-n2-u1 | st | nrt-n2-u1Set | lockset | co:nb-u2=on | co:nb-n2=on |  |
| nrt-n3-u1 | st | nrt-n3-u1Free | unlock | co:nb-n3=on | st:nrt-n3-u1=locked |  |
| nrt-n3-u1 | st | nrt-n3-u1Free | unlock | fb:nd24=off | st:nrt-n3-u1=locked |  |
| nrt-n3-u1 | st | nrt-n3-u1Set | lockset | co:nb-u2=on | co:nb-n3=on |  |
| nrt-n4-u1 | st | nrt-n4-u1Free | unlock | co:nb-n4=on | st:nrt-n4-u1=locked |  |
| nrt-n4-u1 | st | nrt-n4-u1Free | unlock | fb:nd24=off | st:nrt-n4-u1=locked |  |
| nrt-n4-u1 | st | nrt-n4-u1Set | lockset | co:nb-u2=on | co:nb-n4=on |  |
| nrt-n5-u1 | st | nrt-n5-u1Free | unlock | co:nb-n5=on | st:nrt-n5-u1=locked |  |
| nrt-n5-u1 | st | nrt-n5-u1Free | unlock | fb:nd24=off | st:nrt-n5-u1=locked |  |
| nrt-n5-u1 | st | nrt-n5-u1Set | lockset | co:nb-u2=on | co:nb-n5=on |  |
| nrt-n6-u1 | st | nrt-n6-u1Free | unlock | co:nb-n6=on | st:nrt-n6-u1=locked |  |
| nrt-n6-u1 | st | nrt-n6-u1Free | unlock | fb:nd24=off | st:nrt-n6-u1=locked |  |
| nrt-n6-u1 | st | nrt-n6-u1Set | lockset | co:nb-u2=on | co:nb-n6=on |  |
| nrt-n7-u1 | st | nrt-n7-u1Free | unlock | co:nb-n7=on | st:nrt-n7-u1=locked |  |
| nrt-n7-u1 | st | nrt-n7-u1Free | unlock | fb:nd24=off | st:nrt-n7-u1=locked |  |
| nrt-n7-u1 | st | nrt-n7-u1Set | lockset | co:nb-u2=on | co:nb-n7=on |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-i1=on | st:nrt-u1-u2=locked and st:nrt-i2-u1=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-n0=on | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-n1=on | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-n2=on | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-n3=on | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-n4=on | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-n5=on | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-n6=on | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | co:nb-n7=on | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Free | unlock | fb:nd24=off | st:nrt-u1-u2=locked |  |
| nrt-u1-u2 | st | nrt-u1-u2Set | lockset | co:nb-u2=on | (co:nb-n0=on or co:nb-n1=on or co:nb-n2=on or co:nb-n3=on or co:nb-n4=on or co:nb-n5=on or co:nb-n6=on or co:nb-n7=on or co:nb-i1=on) |  |
| nrt-u2-ut | st | nrt-u2-utFree | unlock | co:nb-u2=on | st:nrt-u2-ut=locked |  |
| nrt-u2-ut | st | nrt-u2-utFree | unlock | co:yd03d=off | fb:yd03=false and st:nrt-u2-ut=locked |  |
| nrt-u2-ut | st | nrt-u2-utSet | lockset | co:krt-ki-helper=off | co:noRTup=on |  |
| nrt-u2-ut | st | nrt-u2-utSet | lockset | co:nb-ut=on | co:nb-u2=on and st:krt-ki=unlocked |  |

## Havna (h)

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| hd02 | fb | hd02off | off | co:dirRes=on | - |  |
| htxDir | tx | htxDirSkifte | update | fb:hd02=true | - |  |
| htxDir | tx | htxDirSolberg | update | fb:hd02=false | - |  |

## Other

### 3.2 Actions that don't set a signal

| Target | Type | Action | Command | Trigger | Conditions | Desc |
|---|---|---|---|---|---|---|
| rtb-to | co | rtb-toOff | off | co:rtb-to=on | - |  |
| rtb-to | co | rtb-toOff | off | vr:rtb-toTmr==0 | - |  |
| rtb-to | co | rtb-toOn | on | co:rtb-to=off | (co:nb-in=on or co:nb-i1=on or co:nb-n0=on or co:nb-n1=on or co:nb-n2=on or co:nb-n3=on or co:nb-n4=on or co:nb-n5=on or co:nb-n6=on or co:nb-n7=on or co:nb-u2=on or co:nb-ut=on or co:ib11=on or co:ib12=on or co:ib13=on or co:ib14=on or co:ib15=on or co:ib16=on or co:ib17=on or co:ib18=on or co:ib19=on or co:ib20=on or co:ib21=on or co:ib22=on) |  |
| rtb-toTmr | vr | rtb-toTmrCnt | add | co:rtb-to=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib11=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib12=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib13=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib14=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib15=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib16=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib17=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib18=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib19=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib20=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib21=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:ib22=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-i1=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-in=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-n0=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-n1=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-n2=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-n3=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-n4=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-n5=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-n6=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-n7=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-u2=on | - |  |
| rtb-toTmr | vr | rtb-toTmrRes | value | co:nb-ut=on | - |  |
| rtb-tox | co | rtb-toxGo | off | co:rtb-to=on | vr:rtb-toTmr=>1 |  |

## Action controls that point to a missing action

None.
