# Analysis 1: Layout diff 2026-11-12 vs 2026-11-19

Files compared:

- Old: `20261112232305122-DMJK-Layout.xml`
- New: `20261119232535091-DMJK-Layout.xml`

Tool: `python xmldiff.py OLD.xml NEW.xml xmldiff.txt`. The script matches elements by `id`, or by position when an element has no `id`. It reports added and removed elements, and changed attributes and text. Full output is in `xmldiff.txt`.

## 1. Summary

The script found 168 differences. No elements were added or removed. No `<action>`, `<actionctrl>` condition, route or block definition changed.

The only configuration change is the port addresses of 9 signals. Signal `is03` now has the same port on both outputs, which is almost certainly a typo.

The check against `DMJK-Adresser.pdf` (sections 6 and 7) found 3 errors on the Sigdal - Myra - Mjøndalen stretch:

1. `is03` port2 must be 1006, not 1005.
2. Level crossing output `yoP1` (Myra) must be on 1017, not 1025.
3. Level crossing output `moP1` (Mjøndalen) must be on 1018, not 1026.

It also found that output `soSloc` and signal `ss26` share address 528.

Changed attributes, by count:

| Attribute     | Count |
|---------------|------:|
| `counter`     |    65 |
| `state`       |    25 |
| `switched`    |    21 |
| `wantedstate` |    20 |
| `fieldstate`  |    14 |
| `port1`       |     9 |
| `port2`       |     7 |
| `value`       |     3 |
| `text`        |     2 |
| `rocrailip`   |     1 |
| `rocrailpwd`  |     1 |

## 2. Signal addresses (configuration, affects hardware)

| Signal | Old port1/port2 | New port1/port2 |
|--------|-----------------|-----------------|
| is01   | 1153/1154       | 1001/1002       |
| is02   | 1155/1156       | 1003/1004       |
| is03   | 1157/1158       | **1005/1005**   |
| ys01   | 1057/1058       | 985/986         |
| ys02   | 1075/1076       | 995/996         |
| ys04   | 1059/1060       | 987/988         |
| ys05   | 1073/1074       | 993/994         |
| ys06   | 1061/0          | 989/0           |
| ys07   | 1077/0          | 997/0           |

1. Actions call signals by `id`, not by address. The action logic still runs the same way, but the commands now go to the new decoder addresses.
2. **is03 has port2 = port1 = 1005.** The pattern of the other signals says port2 should be 1006. With both outputs on one port, is03 (a 3-aspect light signal) can't show all aspects correctly. Fix this before you run the layout.
3. The new ports (985 to 1005) don't clash with any other signal, switch or output in the new file.

## 3. Variable `koOccTmr`

`vr[koOccTmr]` changed from 21 to 5. If an action uses this variable as a timer or a condition, this changes behavior. The value can also be runtime state that an action wrote. This analysis doesn't check where `koOccTmr` is set or read.

## 4. Runtime state (no effect on action logic)

1. Sensor `counter` (65 changes): each `actionctrl` counter has the same value as the `counter` on its parent `fb`.
2. Switch `state`, `wantedstate`, `fieldstate` and `switched`: the last position and the switch count.
3. Sensor state `md14` and `nd06` (false to true). Signal `ss22` changed from red to green.
4. Outputs `ioUTy`, `koLF` and `koLFlok` (state and value). Text `htxDir` state changed from true to false.

Rocrail saves these values at shutdown and can restore them at startup. The starting positions then differ, but the logic doesn't.

## 5. Cosmetic and environment changes

1. `rocrailip` changed from 192.168.56.1 to 192.168.1.155, and `rocrailpwd` changed from the Roger user folder to the DMJK user folder. The file now comes from a different PC.
2. The version label changed from `DMJK-Layout-V10, 20261111` to `DMJK-Layout-V10b, 20261114`.
3. Text `mtxDir` changed from "Solberg" to "Skifte".

## 6. Check against DMJK-Adresser.pdf

The PDF was converted to text with `pdftotext -layout DMJK-Adresser.pdf DMJK-Adresser.txt`. The PDF header says "Oppdatert 14. november 2026 - ny signaldekoder kode med flere aspekt og nye adresser". This date matches the new version label `V10b, 20261114`, so the address change is intentional.

How to read the PDF: each name line (for example `ys01 BR`, `ys01 BG`) is one OD-2 aspect. Each DCC address holds 2 aspects, so a signal with 4 name lines uses 2 addresses. The text extraction doesn't always align the names with the address column, so count the name lines from the decoder start address. The Solberg section, which didn't change, confirms this rule: ss27 = 513/514, ss28 = 515, ss01 = 516/517, is13 = 518/519, ss06 = 521/522 and ss22 = 531 all match the XML.

| Signal | Aspects in PDF        | PDF addresses | New XML port1/port2 | Result       |
|--------|-----------------------|---------------|---------------------|--------------|
| ys01   | BR, BG, BY, ----      | 985/986       | 985/986             | Match        |
| ys04   | BR, BG, BY, ----      | 987/988       | 987/988             | Match        |
| ys06   | BR, BG                | 989           | 989/0               | Match        |
| ys05   | BR, BG, BY, ----      | 993/994       | 993/994             | Match        |
| ys02   | BR, BG, BY, ----      | 995/996       | 995/996             | Match        |
| ys07   | BR, BG                | 997           | 997/0               | Match        |
| is01   | IR, IG, IY, ----      | 1001/1002     | 1001/1002           | Match        |
| is02   | FR, FG, FY, ----      | 1003/1004     | 1003/1004           | Match        |
| is03   | IR, IG, IY            | 1005/1006     | 1005/**1005**       | **Mismatch** |

1. The PDF confirms the is03 error: port2 must be 1006, not 1005. With port2 = 1005, the yellow aspect (IY) is sent to the wrong address.
2. The PDF labels the second aspect of is01 as `si01 IG`. This is a typo in the PDF; it belongs to is01.
3. The old addresses (1057 to 1077, 1153 to 1158) don't occur anywhere in the PDF.
4. The PDF doesn't mention `koOccTmr`. Section 3 is still open.

## 7. Full address check: PDF vs new XML

Tool: `python pdfcheck.py DMJK-Adresser.pdf 20261119232535091-DMJK-Layout.xml pdfcheck.txt`. The script runs `pdftotext -raw`, which keeps each table row on one line, so every row carries its own DCC or sensor address. It compares every signal, level-crossing output, switch and detector in the PDF with the new XML:

1. Signals and outputs: the set of DCC addresses vs `sg` `port1`-`port4`, or `co` `port`.
2. Switches: the DCC address vs `sw` `port1`.
3. Detectors: the sensor address vs `fb` `addr`.
4. In reverse: XML objects that use an address the PDF gives to another object of the same kind.

Everything not listed below matches: all signals except is03, all switches and all detectors at Solberg, Skiftegården, Kobbarvik, Mjøndalen, Myra, Sigdal and Norbotten.

### 7.1 Errors on the Sigdal - Myra - Mjøndalen stretch

| Object | Kind                       | PDF        | XML           | Effect                                                     |
|--------|----------------------------|------------|---------------|------------------------------------------------------------|
| is03   | Signal, block `yd08`       | 1005/1006  | 1005/**1005** | Yellow aspect (IY) can't be shown                          |
| yoP1   | Output, level crossing Myra | 1017       | **1025**      | The level crossing at Myra doesn't get the command        |
| moP1   | Output, level crossing Mjøndalen | 1018 | **1026**      | The level crossing at Mjøndalen doesn't get the command   |

1. **is03** sits on Myra block `yd08`, the same block as ys01. With both ports on 1005, the yellow aspect goes to the wrong address. Set `port2` to 1006.
2. **yoP1 and moP1** didn't change between the two XML files. The PDF of 14 November moved them to 1017/1018 (decoder y#3, "Planovergang dekodere, bruker 1 adresse hver"). The XML still uses 1025/1026, so the actions `yoP1on`/`yoP1off` and `moP1on`/`moP1off` send to addresses with no decoder. `yoP1` is driven by sensor `yd05` and switch `yv03`. This is the most likely cause of problems at Myra if the decoders were reprogrammed to the PDF addresses. Set `yoP1` port to 1017 and `moP1` port to 1018.
3. The PDF also lists `moP1` (688) and `yoP1` (689) as detectors on RS-8 m#2. The XML has no sensors on 688 or 689. If these are feedback from the level crossings, they aren't used in Rocrail.

### 7.2 Other findings

1. **Address collision `soSloc` / `ss26`.** Output `soSloc` ("Lokal Sifting (eksperimentell)") uses port 528. The PDF and the XML give 528 to the second address of signal ss26 (527/528). Switching `soSloc` changes the aspect of ss26, and the reverse. This didn't change between the two XML files.
2. **Paired switches on a virtual interface.** The PDF gives one DCC address to two switches: sv11/sv12, sv13/sv14, iv01/iv02, iv14/iv15, iv16/iv17, kv01/kv02, kv04/kv05, mv01/mv02, mv12/mv13 and yv06/yv07. In the XML, the second switch of each pair is on `iid="vrt"` with a port in the 400 range. This looks intentional (the first switch drives the real decoder), so it isn't an error.
3. **Test switches ib11-ib21** ("Togvei-brytere (testoppsett)", sensors 800-810) are `co` objects without an address in the XML. Sensors fb26, fb27 and fb28 use 800, 801 and 803. This is the test setup only.
4. `si01 IG` in the PDF is a typo for is01 (see section 6).

## 8. Not checked

1. Whether any action uses the sensor `counter` as a condition.
2. Where `koOccTmr` is set or read.
3. Signal aspect patterns (`red`, `green`, `yellow` values) against the OD-2 configuration files in the PDF.
4. Route definitions between Sigdal and Mjøndalen. Only the addresses of the objects on the stretch are checked.
