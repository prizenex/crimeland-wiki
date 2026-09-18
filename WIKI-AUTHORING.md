# Як заповнювати вікі CRIMELAND без помилок

Цей документ — **внутрішній гайд для авторів** (`crimeland-wiki`). Мета: описувати в гайдах **лише те, що реально працює на live-сервері**, а не те, що просто лежить у репозиторії `chinazes`.

### Тон: гайдбук всередині RP

Вікі читає **гравець у сесії**, не розробник. Пишемо як довідник мешканця штату:

- **Так:** «Підійди до NPC, **`E`** / **`лівий Alt`** ([Керування](../basics/controls.md))», бліп ![](../.gitbook/assets/blips/419.png), іконка ПКМ ![](../.gitbook/assets/inputs/mouse-rmb.svg), предмет <img src="../.gitbook/assets/mechanic_tablet.png" data-size="line"> → **Використати** в інвентарі
- **Таргет (NPC / об'єкти):** не пиши лише `лівий Alt`. Стандарт: **`E`** / **`лівий Alt`** + посилання на [Керування](../basics/controls.md) — там **звичайний** (кружечок + `E`) та **імерсивний** (`Alt` + ЛКМ). **Не згадуй** назву ресурсу таргета.
- **Ні:** назви ресурсів, `vector3`, `TriggerServerEvent`, папки `[job]`, **команди чату** (`/tablet`, `/multijob`, `/furniture` …)

> Гравці **не користуються `/командами`**. Якщо дія відкривається предметом — показуй **іконку з `.gitbook/assets/`** і шлях: `Tab` → ПКМ → **Використати**. Якщо дія в меню — **`F1`**, **`F7`**, радіальне меню. Команди в конфігу скрипта — лише для авторів при звірці, не для тексту гайду.

Кожна стаття — **сценарій у світі**: де на мапі, що натиснути, що отримаєш.

---

## 1. Головне правило

> **Джерело правди — лише ресурси, які стартують через ланцюг `server.cfg`.**

Якщо скрипт є в `resources/`, але **не ensure-иться** (або ensure закоментований) — **не описуй його механіку** у player-facing вікі.

Типова помилка: у репо лежать **два** схожих ресурси (старий і новий), а на сервері активний лише один. Автор читає не той — гравець отримує неправильну клавішу, ціну або предмет.

---

## 2. Ланцюг старту (що вважати активним)

### 2.1. `server.cfg` — основа

Усі рядки виду `ensure <назва>` **без `#` на початку** — це активні ресурси.

**Папки** (`ensure [crime]`, `ensure [glovo]`, `ensure [unit]` тощо) стартують **усі** підпапки з валідним `fxmanifest.lua` всередині.

**Закоментовані** рядки (`# ensure illenium-appearance`) — ресурс **не працює**, навіть якщо файли є в репо.

### 2.2. Підключені cfg-файли

| Файл | Що робить | Чи стартує ресурси |
|------|-----------|-------------------|
| `server.cfg` | ensure/stop ресурсів, convars | **Так** |
| `miner.cfg` | convars шахтарства (`miner_*`) | **Ні** — лише налаштування |
| `ivan.cfg` | ACE, permissions, convars | **Ні** — лише права/налаштування |
| `unit.cfg` | список ensure для unit-ресурсів | **Зараз не exec'иться** з `server.cfg` |

> **Увага:** `unit.cfg` існує як довідник, але в поточному `server.cfg` **немає** `exec unit.cfg`. Ресурси з `unit.cfg` вважаються активними **лише якщо** вони також потрапляють у ensured-папку (наприклад `sky_battlepass` у `[unit]`) або мають окремий `ensure` у `server.cfg`.

### 2.3. Активні ensure-групи (орієнтир)

Перевіряй актуальний список у `chinazes/server.cfg`. На момент написання гайду ключові групи:

```
ensure ox_inventory
ensure rcore_clothing          # illenium-appearance — закоментований
ensure [qb], [codem], [glovo], [addon], [phone], [crime], [job], [murols], [vms], [rtx]
ensure emotes
ensure [unit], [jg]
exec miner.cfg
exec ivan.cfg
```

**Не активні** (приклади з репо, які часто плутають):

| У репо | Чому не брати |
|--------|---------------|
| `illenium-appearance` | `# ensure` у `server.cfg`; активний `rcore_clothing` |
| `rpemotes-reborn` | не ensure-иться; емоції — `cylex_animmenuv2` через `[addon]` |
| `bp_skillsystem` | у `[dontEnsure]`, немає ensure |
| ресурси з `# ensure` у `unit.cfg` | не стартують, поки немає ensure в `server.cfg` |

---

## 3. Workflow перевірки перед написанням сторінки

Виконуй **у такому порядку**:

### Крок 1 — Знайти механіку в ensured-ресурсі

```powershell
# Активні ensure у server.cfg (без коментарів)
Select-String -Path 'F:\git\chinazes\server.cfg' -Pattern '^\s*ensure ' |
  Where-Object { $_.Line -notmatch '^\s*#' }

# Список ресурсів у папці (приклад: crime)
Get-ChildItem -LiteralPath 'F:\git\chinazes\resources\[crime]' -Directory |
  Where-Object { Test-Path (Join-Path $_.FullName 'fxmanifest.lua') } |
  Select-Object -ExpandProperty Name
```

Якщо тема стосується кількох скриптів — шукай **усі** через `rg` у ensured-папках, не по всьому `resources/`.

### Крок 2 — Читати відкриті конфіги

Пріоритет файлів:

1. `config.lua`, `config/*.lua`, `shared/config.lua`
2. `resources/ox_inventory/data/items.lua` — предмети, описи, вага (ox_inventory завжди ensured)
3. `resources/ox_inventory/data/shops.lua` — ціни магазинів
4. convars у `server.cfg` / `miner.cfg` (клавіші інвентаря, голос, шахтарство)

Escrow-файли (зашифровані) — читай **лише відкриті** частини: `config.lua`, `escrow_ignore` у `fxmanifest.lua`.

### Крок 3 — Перевірити кастомні обгортки `[glovo]` / `[unit]`

Часто **реальна** клавіша або логіка сидить не в escrow-скрипті, а в кастомному коді:

| Тема | Основний ресурс | Де шукати override |
|------|-----------------|-------------------|
| Батлпас | `sky_battlepass` | `crimeland_sky_startquest` — keybind **F10** |
| Щоденні квести BP | `sky_battlepass` | `crimeland_sky_startquest/config.lua` |
| Стартові предмети | `ZSX_Multicharacter` | `ox_inventory` items + multichar config |

**Правило:** якщо `[glovo]`/`[unit]` змінює UX (клавіша, меню, нагорода) — у вікі пиши **те, що бачить гравець**, тобто поведінку після обгортки.

### Крок 4 — Звірити предмети та картинки

- Назва предмета в гайді = `name` з `ox_inventory/data/items.lua`
- Картинка: копіюй з `chinazes/resources/ox_inventory/web/images/<item>.png` → `crimeland-wiki/.gitbook/assets/<item>.png`
- **Іконки в таблицях залишаємо** — не прибирати, лише зменшувати.
- Формат: `<img src="../.gitbook/assets/item_name.png" alt="Назва" data-size="line"> Назва` в тій самій клітинці, що й текст.
- GitBook **не** поважає `width="24"` у таблицях (іконка лишається величезною). **`data-size="line"`** — єдиний правильний inline-розмір.
- **Ніколи** `data-size="original"` і голий `![](path)` для предметів у таблицях — рендериться на всю клітинку.

### Крок 5 — Не писати назви скриптів гравцю

У тексті для гравців **заборонено**: `ox_inventory`, `qb-target`, `sky_battlepass`, `tgiann-target` тощо.

Допустимо в цьому гайді (для авторів) — для навігації по репо.

---

## 4. Стиль сторінок (референс)

**Еталон оформлення:** [`crime/atms.md`](crime/atms.md)

### Frontmatter (обов'язково)

```markdown
---
description: Одне речення — що дізнається гравець на сторінці.
icon: font-awesome-icon-name
---
```

Іконки: [Font Awesome icons for GitBook](https://fontawesome.com/icons) — kebab-case (`money-bill-transfer`, `car`, `heart`).

### Структура контенту

1. **Короткий вступ** — що це і навіщо гравцю
2. **Таблиці** — числа, шанси, ціни, cooldown (як у atms.md)
3. **Покрокові блоки** — `###` заголовки + списки
4. **Предмети з іконками** — inline `<img>` або markdown-зображення
5. **`{% hint style="info" %}`** — важливі нюанси, ризики, винятки

### Мова

- Player-facing текст: **українська**
- Без вульгаризмів
- Конкретні числа з конфігу, не «приблизно» / «багато»

### Скріншоти UI

- UI-скріни → `.gitbook/assets/` з зрозумілими іменами (`battlepass-daily.png`)
- Не коміть важкі `.zip` з сирими матеріалами в корінь розділу — лише готові assets

### Бліпи GTA (орієнтири на мапі)

**Обов’язково:** кожна **локація на мапі** в статті (паркінг, магазин, штрафмайданчик, робота, зона активності) має бути позначена **іконкою бліпа** — той самий `sprite`, що в ensured-конфігу (`SetBlipSprite` / `blip.id`). Без бліпа гравець не впізнає точку на `P`.

Щоб гравцю було легше знайти точку, вставляйте **іконку бліпа** поруч із описом локації — той самий символ, що на мапі в грі.

| Що | Де |
| --- | --- |
| PNG-файли | `.gitbook/assets/blips/{ID}.png` — `{ID}` = `sprite` з конфігу (`SetBlipSprite`) |
| Довідник ID | [FiveM Blips](https://docs.fivem.net/docs/game-references/blips/) |
| Приклад у тексті | `![](../.gitbook/assets/blips/475.png)` біля «будівля з апартаментами» |

**Повний пак** уже в репо: `.gitbook/assets/blips/` (**767** PNG, ID `1`–`918`, пропуски — неіснуючі sprite у [bb_blip_creator](https://github.com/Baashabhai-studio/bb_blip_creator)). Для статті просто вставляйте `![](../.gitbook/assets/blips/{ID}.png)`.

> **Пастка:** ID у файлі (`475.png`) має збігатися з `sprite` у `vms_housing` / `qs-housing` / іншому ensured-конфігу — не вигадуйте іконку «на око».

### Іконки клавіш і миші

У грі (онбординг, меню емоутів) кнопки показуються як **чіпи**: клавіші — білий прямокутник, миша — силует із **підсвіченою** ЛКМ / ПКМ / колесом (акцентний колір HUD).

| Тип | Файл у вікі | Коли вставляти |
| --- | --- | --- |
| ЛКМ | `.gitbook/assets/inputs/mouse-lmb.svg` | лівий клік, «використати», запуск емоуту |
| ПКМ | `.gitbook/assets/inputs/mouse-rmb.svg` | правий клік, контекстне меню, **спільні емоути** |
| СКМ | `.gitbook/assets/inputs/mouse-mmb.svg` | колесо миші, «обрати місце» в AnimPos |
| Клавіша | текст у `<kbd>` або «**TAB**» | звичайні бінди |

Приклад у markdown (з `character/`):

```markdown
Натисніть **ПКМ** ![](../.gitbook/assets/inputs/mouse-rmb.svg) на гравця.
```

Джерело SVG: `[glovo]/crimeland_onboarding/html/script.js` (`MOUSE_SVG`). У `crimeland_hud` лише **текстові** чіпи клавіш (`.keyhint-key`), без іконок миші.

---

## 5. Сторінки, які не чіпати без окремого запиту

Готові / узгоджені сторінки (не переписувати «про всяк випадок»):

- `basics/phone.md`
- `crime/atms.md`, `crime/weed.md`, `crime/twenty-four-seven.md`
- `crime/contract-tablet.md`, `crime/houses.md`, `crime/jewelry-store.md`
- `crime/car-theft.md`, `crime/containers.md`

Якщо механіка на сервері змінилась — спочатку звір ensured-конфіг, потім точково онови потрібний блок.

---

## 6. Типові помилки (античеклист)

| Тема | ❌ Неправильно | ✅ Правильно | Де перевірити |
|------|---------------|-------------|---------------|
| Батлпас | `/battlepass` у конфігу | **F10** (у гайді — лише клавіша, без чату) | `crimeland_sky_startquest/client.lua` |
| Емоції | F6, rpemotes | **U** — меню емоцій | `[addon]/cylex_animmenuv2/config.lua` (`OpenKey`) |
| Зовнішність | ціни illenium | ціни **rcore_clothing** | `rcore_clothing` configs (illenium закоментований) |
| Інвентар | «TAB» без перевірки | TAB / F2 / Z — з convar | `server.cfg` → `inventory:keys` |
| Голос | довільна клавіша | **Ґ** (GRAVE) | `server.cfg` → `voice_defaultCycle` |
| Одяг / барбер | illenium ціни | rcore ціни та UX | активний `rcore_clothing` |
| Дикий канабіс | «будь-які сорти» | лише активні рецепти в config | `[crime]/kq_wild_cannabis/config.lua` |
| Маркетплейс / ринок авто | вигадані % | з config конкретного ресурсу | `ms-marketplace`, `qb-vehiclesales` |
| Документи в ЦНАП | **50$** | **2 500$** ID / ліцензія; **10 000$** бізнес-карта | `codem-wallet` → `CardPrices` |
| Шахтарство | дефолти з README мода | convars `miner_*` | `miner.cfg` |

---

## 7. Чеклист перед збереженням сторінки

- [ ] Знайшов ensured-ресурс(и) для теми в `server.cfg`
- [ ] Не використав закоментований або `[dontEnsure]` ресурс
- [ ] Перевірив `[glovo]` / `[unit]` на override (клавіші, меню, нагороди)
- [ ] Усі числа (ціни, %, cooldown, шанси) — з відкритого config, не з пам'яті
- [ ] Предмети існують у `ox_inventory/data/items.lua`
- [ ] Картинки предметів скопійовані в `.gitbook/assets/`
- [ ] Frontmatter: `description` + `icon`
- [ ] Немає назв скриптів у player-facing тексті
- [ ] Стиль узгоджений з `crime/atms.md`
- [ ] Сторінка не зі списку «не чіпати» — або зміна обґрунтована зміною на сервері

---

## 8. Приклад: як написати сторінку з нуля

**Тема:** «Спортзал / добавки»

1. `server.cfg` → `ensure [rtx]` → ресурс `rtx_gym`
2. Читаю `resources/[rtx]/rtx_gym/config.lua` → `Config.Supplements`
3. Перевіряю, чи `[glovo]` не змінює ціни/локації
4. Предмети добавок у `ox_inventory/data/items.lua` → копіюю png
5. Пишу `character/sport.md`: таблиця бонусів, тривалість, як купити/використати
6. Hint: добавка діє N хвилин — число з config

---

## 9. Мапінг: розділи вікі → ensured-ресурси

Нижче — **головна таблиця для авторів**: яка сторінка вікі з якого скрипта бере механіку.  
Шляхи — від `chinazes/resources/`. Колонка **ensure** показує, як ресурс потрапляє на сервер.

**Легенда ensure:**

| Тип | Приклад |
|-----|---------|
| `папка` | `ensure [crime]` → усі ресурси з `fxmanifest.lua` у папці |
| `окремий` | `ensure ox_inventory` у `server.cfg` |
| `stop` | `stop 17mov_JobCenter` — ресурс **не** працює, навіть якщо лежить у репо |
| `закоментовано` | `# ensure illenium-appearance` — **не** активний |
| `не ensure` | лежить у `[dontEnsure]` / `[nedoroblene]` — **ігнорувати** для вікі |

### 9.1. Старт / Основи

| Сторінка вікі | Основні ресурси | Config / override | Ensure |
|---------------|-----------------|-------------------|--------|
| `getting-started/connect.md` | — (FiveM-клієнт) | — | — |
| `getting-started/character.md` | `ZSX_Multicharacter`, `rcore_clothing` | `ZSX_Multicharacter/shared/config.lua` | окремий + `[addon]` |
| `getting-started/first-steps.md` | `crimeland_onboarding`, `crimeland_starter_apartments`, `ms-menu` | `ms-menu/config/quests_config.lua` | `[glovo]`, `[murols]` |
| `basics/rules.md` | `ms-menu` (FAQ) | `ms-menu/config/faq_config.lua` | `[murols]` |
| `basics/server-menu.md` | `ms-menu`, `Tebex-FiveM` | `ms-menu/config/config.lua` (`Config.MenuKey = F4`) | `[murols]` + окремий |
| `basics/battlepass.md` | `sky_battlepass`, **`crimeland_sky_startquest`** | BP: `[unit]/sky_battlepass/config/`; **F10**: `[glovo]/crimeland_sky_startquest/client.lua` | `[unit]` + `[glovo]` |
| `character/inventory.md` | `ox_inventory`, `pinkFrog_inventoryAddon` | `server.cfg` → `inventory:keys`; `ox_inventory/data/*.lua` | окремий + `[addon]` |
| `basics/phone.md` | `lb-phone`, `lb-phoneprop`, `lb_powerbank` | `lb-phone/config/*` | `[phone]` + `[unit]` |
| `basics/radio.md` | `pma-voice`, `qb-radio` | `server.cfg` → `voice_defaultCycle` (GRAVE) | `[voice]` |
| `basics/controls.md` | `ZSX_UIV2`, `qb-core` keybinds | convars + `qb-core` shared | окремий + `[qb]` |
| `basics/bank.md` | `qb-banking`, `codem-wallet` (картки) | `[qb]/qb-banking/config.lua` | `[qb]` + `[codem]` |
| `basics/city-hall.md` | **`crimeland_jobcenter`**, `codem-wallet`, `ms-menu` | `[glovo]/crimeland_jobcenter/`; **не** `qb-cityhall` (`[nedoroblene]`) | `[glovo]` |
| `basics/documents.md` | `codem-wallet`, `0r-idcard`, `ZSX_Multicharacter` | `[codem]/codem-wallet/shared/config.lua` | `[codem]` + `[addon]` |
| `basics/shops.md` | `lc_stores`, `lc_utils` | `lc_stores/config.lua` | окремий |
| `basics/marketplace.md` | `ms-marketplace` | `[murols]/ms-marketplace/config.lua` | `[murols]` |

> **Пастка:** `17mov_JobCenter` у `server.cfg` має `stop` — для центру зайнятості дивись **`crimeland_jobcenter`**, не 17mov.  
> **Пастка:** `qb-cityhall` у `[nedoroblene]` — **не ensure**, не використовувати.

### 9.2. Транспорт

| Сторінка вікі | Основні ресурси | Config / override | Ensure |
|---------------|-----------------|-------------------|--------|
| `transport/driving-school.md` | `vms_driveschoolv2` | `[vms]/vms_driveschoolv2/config/config.lua` | `[vms]` |
| `transport/rental.md` | `xCarRent` | `[codem]/xCarRent/config.lua` | `[codem]` |
| `transport/dealerships.md` | `jg-dealerships-v2` | `[jg]/jg-dealerships-v2/config/*` | `[jg]` |
| `transport/parking.md` | `jg-advancedgarages`, `qb_garage_limit` | `[qb]/jg-advancedgarages/config.lua` | `[qb]` + `[glovo]` |
| `transport/tuning.md` | `jg-mechanic` | `[jg]/jg-mechanic/config/*` | `[jg]` |
| `transport/racing.md` | **`frkn-racingv2`** (предмет `racing_gps`) | `[mods]/frkn-racingv2/shared/config.lua` | `[mods]` |
| `transport/drift.md` | `DLDriftZone` | `[mods]/[DriftZoneQB]/DLDriftZone/config/` | `[mods]` |
| `transport/market.md` | `qb-vehiclesales` | `[qb]/qb-vehiclesales/config.lua` | `[qb]` |
| `transport/trailers.md` | `DLTrailers`, `DLTow` | `[mods]/[DL]/DLTrailers/`, `[mods]/[DL]/DLTow/` | `[mods]` |
| `transport/off-road.md` | `kq_realoffroad`, `kq_towing2` | `[mods]/kq_realoffroad/`, `[mods]/kq_towing2/` | `[mods]` |

> **Пастка:** `cw-racingapp` у `[dontEnsure]` + `unit.cfg` **не exec'иться** — для гонок дивись **`frkn-racingv2`**.  
> **Пастка:** `vms_vehicleshop` у `[nedoroblene]` — салони через **`jg-dealerships-v2`**.

### 9.3. Персонаж

| Сторінка вікі | Основні ресурси | Config / override | Ensure |
|---------------|-----------------|-------------------|--------|
| `character/statuses.md` | `ZSX_UIV2`, `qb-smallresources`, `qb-stress-handler`, `rtx_gym` | HUD: `ZSX_UIV2/shared/ui_cfg/config_hud.lua`; стати: **F1** → Фізуха → Стати | окремий + `[qb]` + `[rtx]` |
| `controls/radial.md` | `qb-radialmenu` | `[qb]/qb-radialmenu/config.lua` | `[qb]` |
| `character/animations.md` | **`cylex_animmenuv2`** (`OpenKey = U`) | `[addon]/cylex_animmenuv2/config.lua` | `[addon]` |
| `character/sport.md` | `rtx_gym` | `[rtx]/rtx_gym/config.lua` → `Config.Supplements` | `[rtx]` |
| `character/appearance.md` | **`rcore_clothing`** | `[addon]/rcore_clothing/configs/*` | `[addon]` |
| `character/clothing.md` | `rcore_clothing`, `item_clothes` | rcore configs + `[glovo]/item_clothes/` | `[addon]` + `[glovo]` |
| `character/pets.md` | `cdev_pets` (+ `cdev_*` assets) | `[cdev_pets]/cdev_pets/public/config/config.lua`, `shop.lua` | `[cdev_pets]` + `[cdev_assets]` |
| `character/tattoo-salon.md` | `rcore_tattoos` | `[addon]/rcore_tattoos/config.lua` | `[addon]` |
| `character/nail-salon.md` | `dd-nailshopV2` (+ DLC) | `[addon]/dd-nailshopV2/config.lua` | `[addon]` |
| `character/marriage.md` | `uniqers-marriage` | `[unit]/uniqers-marriage/shared/config.lua` | `[unit]` |
| `character/love-menu.md` | `ak4y-arcadeMachines` (lovemeter) | `[games]/[lunapark]/ak4y-arcadeMachines/configs/lovemeter/` | `[games]` |

> **Пастка:** `illenium-appearance` — `# ensure` у `server.cfg`.  
> **Пастка:** `rpemotes` / F6 — **не** ensure; емоції = **`cylex_animmenuv2`**.

### 9.4. Будинок

| Сторінка вікі | Основні ресурси | Config / override | Ensure |
|---------------|-----------------|-------------------|--------|
| `housing/first-home.md` | `qs-housing`, `vms_housing`, `crimeland_starter_apartments` | `[housing]/qs-housing/shared/config.lua`; `[vms_housing]/vms_housing/` | `[housing]` + `[vms_housing]` + `[glovo]` |
| `housing/real-estate-market.md` | `qs-housing` | qs-housing config (ринок / продаж) | `[housing]` |
| `housing/house-management.md` | `qs-housing`, `lyn-homeowner` | qs-housing + `[unit]/lyn-homeowner/` | `[housing]` + `[unit]` |
| `housing/decorating.md` | `qs-housing`, `qs-crafting` (меблі) | `[housing]/[dlc]/`, `[crafting]/qs-crafting/` | `[housing]` + `[crafting]` |

### 9.5. Бізнес

| Сторінка вікі | Основні ресурси | Config / override | Ensure |
|---------------|-----------------|-------------------|--------|
| `business/twenty-four-seven.md` | `lc_stores` | `lc_stores/config.lua` (player-owned shops) | окремий |
| `business/gas-station.md` | `lc_gas_stations`, `lc_fuel` | `[addon]/lc_gas_stations/config.lua` | `[addon]` |
| `business/factory.md` | `lc_factories` | `[job]/lc_factories/config.lua` | `[job]` |
| `business/cafe.md` | `crimeland_cat_cafe`, `crimeland_coffeebean`, `lc_stores` | `[glovo]/crimeland_* /config.lua` | `[glovo]` + `lc_stores` |
| `business/showroom.md` | `jg-dealerships-v2` (бізнес-шоурум) | jg-dealerships config | `[jg]` |
| `business/auto-repair-shop.md` | `jg-mechanic` | jg-mechanic business zones | `[jg]` |

### 9.6. Розваги

| Сторінка вікі | Основні ресурси | Config / override | Ensure |
|---------------|-----------------|-------------------|--------|
| `entertainment/casino.md` | `rcore_casino`, `rcore_casino_assets`, `customroulette` | `rcore_casino/config.lua` | окремий |
| `entertainment/billiards.md` | `u_pool` | `[games]/u_pool/config.lua` | `[games]` |
| `entertainment/tennis.md` | `rcore_tennis` | `[games]/rcore_tennis/config.lua` | `[games]` |
| `entertainment/golf.md` | `rcore_golf` | `[games]/rcore_golf/config.lua` | `[games]` |
| `entertainment/basketball.md` | `BodhixBall` | `[bdx]/BodhixBall/` | окремий |
| `entertainment/bmx.md` | `BDX-Bmx`, `BDX-Sport-Hub` | BDX configs | окремий |
| `entertainment/roller-skates.md` | `BDX-Rollers` | BDX configs | окремий |
| `entertainment/skateboard.md` | `BDX-Skate` | BDX configs | окремий |
| `entertainment/ice-skates.md` | `BDX-Ice-Skate` | — | **закоментовано** в `server.cfg` |
| `entertainment/snowboard.md` | `BDX-Snowboarding`, `BDX-Ski` | — | **закоментовано** в `server.cfg` |
| `entertainment/parkour.md` | `BodhixPK` | `[bdx]/BodhixPK/` | окремий |
| `entertainment/martial-arts.md` | `BDX-Fighting` | BDX configs | окремий |

> Перед оновленням зимових сторінок перевір `#ensure BDX-Ice-Skate` / `BDX-Snowboarding` у `server.cfg`.

### 9.7. Роботи

| Сторінка вікі | Ресурс | Config | Ensure |
|---------------|--------|--------|--------|
| `jobs/cleaner.md` | `17mov_GarbageCollector` | `[job]/17mov_GarbageCollector/Config.lua` | `[job]` |
| `jobs/window-cleaner.md` | `17mov_WindowCleaning` | Config.lua | `[job]` |
| `jobs/courier.md` | `randol_pizzajob` / `qs-newspaperjob` | перевір активний job у config | `[job]` |
| `jobs/taxi-driver.md` | `codem-taxijob` | `[job]/codem-taxijob/config.lua` | `[job]` |
| `jobs/bus-driver.md` | `gg_busjob` | config | `[job]` |
| `jobs/trucker.md` | `lc_truck_logistics` | `[job]/lc_truck_logistics/config.lua` | `[job]` |
| `jobs/builder.md` | `17mov_BuilderJob` | Config.lua | `[job]` |
| `jobs/electrician.md` | `17mov_Electrician` | Config.lua | `[job]` |
| `jobs/sawmill.md` | `17mov_Lumberjack` | Config.lua | `[job]` |
| `jobs/gardening.md` | `tw-gardenerv2` | `[job]/tw-gardenerv2/config.lua` | `[job]` |
| `jobs/farming.md` | `0r-farming-v2` | `[job]/[farming]/0r-farming-v2/` | `[job]` |
| `jobs/moonshining.md` | `0r-farming-v2` (brewing) | `[job]/[farming]/0r-farming-v2/core/brewing/config.lua` | `[job]` |
| `jobs/hunting.md` | `wais-hunting`, `boii_hunting` | wais + boii configs | `[job]` + окремий |
| `jobs/fishing.md` | `lc_fishing_simulator` | `[job]/lc_fishing_simulator/config.lua` | `[job]` |
| `jobs/miner.md` | `aquiver-mining-script-ox.pack` | `miner.cfg` (convars) + pack config | `[job]` + `exec miner.cfg` |
| `jobs/firefighter.md` | `enyo-firefighter`, `rescue_script` | configs | `[job]` |
| `jobs/pilot.md` | `pickle_airport`, `vms_flightschoolv2` | `[job]/pickle_airport/`; `[vms]/vms_flightschoolv2/` | `[job]` + `[vms]` |
| `jobs/mechanic.md` | `jg-mechanic`, `qb-towjob` | jg-mechanic job zones | `[jg]` + `[qb]` |

> **Пастка:** `boii-farming` у `[dontEnsure]` — самогон через **`0r-farming-v2`**, не boii-farming.

### 9.8. Кримінал

| Сторінка вікі | Основні ресурси | Config / override | Ensure |
|---------------|-----------------|-------------------|--------|
| `crime/gangs.md` | `core_gangs` | `[crime]/core_gangs/config.lua` | `[crime]` |
| `crime/territory-war.md` | `core_gangs`, `crimeland_startwar` | core_gangs + `[glovo]/crimeland_startwar/` | `[crime]` + `[glovo]` |
| `crime/lockpick.md` | `t3_lockpick`, `qb-vehiclekeys`, `ox_inventory` items | `[standalone]/t3_lockpick/`; vehiclekeys config | `[standalone]` + `[qb]` |
| `crime/robbery-interaction.md` | `crimeland_hostage`, `qb-policejob` | `[glovo]/crimeland_hostage/config/` | `[glovo]` + `[qb]` |
| `crime/contract-tablet.md` | `lunar_heistcontracts` | `[crime]/[lunar]/lunar_heistcontracts/config/` | `[crime]` |
| `crime/twenty-four-seven.md` | `qb-storerobbery` | `[qb]/qb-storerobbery/config.lua` | `[qb]` |
| `crime/jewelry-store.md` | `qb-jewelery` | `[qb]/qb-jewelery/config.lua` | `[qb]` |
| `crime/atms.md` | `projectx-atmrobbery` | `[crime]/[projectx-atmrobbery]/projectx-atmrobbery/config.lua` | `[crime]` |
| `crime/car-theft.md` | `inside-carthief`, `kq_carheist`, lunar `boosting` | відповідні configs | `[crime]` |
| `crime/houses.md` | `vms_houserobberies` | `[vms]/vms_houserobberies/config/` | `[vms]` |
| `crime/containers.md` | lunar `cargo` contract | `config/contracts/cargo.lua` | `[crime]` |
| `crime/bank-robbery.md` | lunar `fleeca`, `paleto`, `pacific` | `config/contracts/*.lua` | `[crime]` |
| `crime/casino-robbery.md` | lunar `casino` contract | `config/contracts/casino.lua` | `[crime]` |
| `crime/big-safe-robbery.md` | `rm_unionheist` | `[crime]/rm_unionheist/config.lua` | `[crime]` |
| `crime/underground-vault-robbery.md` | `rm_vaultheist` | `[crime]/rm_vaultheist/cfg.lua` | `[crime]` |
| `crime/weed.md` | `kq_weed`, `kq_wild_cannabis` | обидва config у `[crime]/kq_*` | `[crime]` |
| `crime/coke.md` | `core_gangs` (зони переробки/збуту) | `[crime]/core_gangs/config.lua` → coke zones | `[crime]` |
| `crime/heisenberg.md` | `kq_meth` | `[crime]/kq_meth/config.lua` | `[crime]` |
| `crime/illegal-sales.md` | `op-drugselling`, `core_gangs` | op-drugselling + gang sell zones | `[crime]` |
| `crime/money-laundering.md` | `drc_moneywash` | `[crime]/drc_moneywash/shared/sh_config.lua` | `[crime]` |

> Більшість банків / контейнерів / casino-heist — **контракти** `lunar_heistcontracts`, не окремі rm_* (крім Union і Vault).

### 9.9. Поліція / EMS / Закони

| Сторінка вікі | Основні ресурси | Config / override | Ensure |
|---------------|-----------------|-------------------|--------|
| `police/getting-started.md` | `qb-policejob`, `ND_Police` | qb-policejob + `ND_Police/data/config.lua` | `[qb]` + окремий |
| `police/officer-guide.md` | `qb-policejob`, `ps-mdt` | `[unit]/ps-mdt/shared/config.lua` | `[qb]` + `[unit]` |
| `police/standard-sentences.md` | — (RP / статичний текст) | узгоджувати з `laws/` | — |
| `police/database-terminal.md` | `ps-mdt` | ps-mdt config | `[unit]` |
| `police/radar-scanner.md` | `wk_wars2x` | `[mods]/wk_wars2x/config.lua` | `[mods]` |
| `police/forensics.md` | `ND_Police` (GSR, evidence) | `ND_Police/data/evidence.lua` | окремий |
| `police/drone.md` | `future_drone` | `[mods]/future_drone/config.lua` | `[mods]` |
| `police/k9.md` | `cdev_pets` (+ `cdev_*` assets) | `[cdev_pets]/cdev_pets/` | `[cdev_pets]` + `[cdev_assets]` |
| `ems/getting-started.md` | `ak47_qb_ambulancejob` | `[qb]/ak47_qb_ambulancejob/config.lua` | `[qb]` |
| `ems/equipment.md` | `ak47_qb_ambulancejob`, `firstaid3`, `enyo-medical` | configs | `[qb]` + `[unit]` + `[job]` |
| `ems/diseases.md` | `enyo-medical`, `g4_addiction`, `ak47_qb_ambulancejob` | enyo-medical + g4_addiction configs | `[job]` + `[crime]` |
| `laws/*.md` | `crimeland_docs` (in-game читання) | `[glovo]/crimeland_docs/config.lua` (Google Doc URLs) | `[glovo]` |

### 9.10. Спільна інфраструктура (не писати гравцю, але знати автору)

| Ресурс | Роль | Ensure |
|--------|------|--------|
| `qb-core` | framework, jobs, metadata | `[qb]` |
| `oxmysql`, `ox_lib` | DB, UI lib | окремий |
| `tgiann-target` | target (`exports['qb-target']`) | `[qb]` |
| `ps-dispatch` | виклики поліції для heist | `[mods]` |
| `kq_link` | бібліотека KQ-скриптів | `[standalone]` |
| `lunar_bridge`, `lunar_minigames` | залежності heist contracts | `[crime]` |
| `cdev_lib` | залежність pets | окремий |
| `lc_utils` | залежність lc_stores / lc_factories | окремий |
| `emotes` | stream/props для емоцій (меню — `cylex_animmenuv2`) | окремий |
| `inventory_shield`, `ms-cheatdetection` | античит | окремий + `[murols]` |

---

## 10. Повний перелік ensured-папок (довідник)

Згенеровано з `server.cfg` + рекурсивний пошук `fxmanifest.lua`.  
Оновлюй після зміни ensure:

```powershell
$base = 'F:\git\chinazes\resources'
$folders = @('[qb]','[standalone]','[voice]','[codem]','[glovo]','[addon]','[phone]',
  '[vms_housing]','[cdev_assets]','[cdev_pets]','[housing]','[mods]','[crafting]',
  '[crime]','[job]','[murols]','[vms]','[rtx]','[games]','[props]','[weapons]','[jg]','[unit]')
foreach ($f in $folders) {
  $path = Join-Path $base $f
  $names = Get-ChildItem -LiteralPath $path -Recurse -Filter 'fxmanifest.lua' |
    ForEach-Object { $_.DirectoryName.Substring($path.Length).TrimStart('\').Split('\')[0] } |
    Sort-Object -Unique
  "$f ($($names.Count)): $($names -join ', ')"
}
```

### Окремі ensure у `server.cfg` (не папки)

`oxmysql`, `ox_lib`, `qb-core`, `ox_inventory`, `rcore_clothing`, `ZSX_UIV2`, `ZSX_Multicharacter`, `ND_Police`, `emotes`, `cdev_lib`, `lc_utils`, `lc_stores`, `boii_hunting`, `rcore_casino`, `rcore_casino_assets`, `customroulette`, `Tebex-FiveM`, `BDX-Sport-Hub`, `BDX-Fighting`, `BDX-Bmx`, `BDX-Skate`, `BDX-Rollers`, `BodhixBall`, `BodhixPK`, `pickle_weaponthrowing`, `kq_brakeoverheat`, `ms-governorelections`, `inventory_shield`, `DLCiplLoader`, `as_mapdata`, MLO (`patoche_*`), тощо.

### Кількість ресурсів по папках (snapshot)

| Папка | К-сть | Примітка для вікі |
|-------|-------|-------------------|
| `[qb]` | 34 | банк, поліція, гаражі, storerobbery, jewelery |
| `[crime]` | 22 | весь кримінал + lunar contracts |
| `[glovo]` | 39 | кастомні override — **завжди перевіряй** |
| `[job]` | 28 | усі роботи |
| `[mods]` | 56 | гонки, дріфт, dispatch, drone, radar |
| `[addon]` | 24 | одяг, тату, nail, емоції, АЗС |
| `[murols]` | 17 | ms-menu, marketplace |
| `[unit]` | 25 | battlepass, marriage, mdt |
| `[games]` | 10 | теніс, гольф, більярд, love-meter |
| `[housing]` | 5 | qs-housing + DLC props |
| `[jg]` | 5 | салони, тюнінг, mechanic |
| `[vms]` | 6 | автошкола, house robberies, flights |
| `[rtx]` | 2 | спортзал |
| `[codem]` | 2 | оренда, гаманець |
| `[phone]` | 4 | lb-phone |
| `[standalone]` | 33 | libs, lockpick, oxmysql |
| `[voice]` | 2 | голос + рація |
| `[crafting]` | 1 | qs-crafting |
| `[props]` / `[weapons]` | 9 / 3 | контент, не геймплей-гайди |

---

## 11. Де що лежить (швидка карта)

| Що описуємо | Репо chinazes | Вікі |
|-------------|---------------|------|
| Механіка, ціни, клавіші | `server.cfg` + ensured `config.lua` | `*.md` у відповідному розділі |
| Мапінг сторінка → скрипт | цей файл §9 | `SUMMARY.md` |
| Предмети | `ox_inventory/data/items.lua` | таблиці + `.gitbook/assets/` |
| Структура розділів | — | `SUMMARY.md`, `структура.md` |
| Стиль | — | `crime/atms.md`, цей файл |

**Репозиторії:**

- Код сервера: `F:\git\chinazes`
- Вікі: `F:\git\crimeland-wiki`

---

## 12. Для AI / Cursor

При автозаповненні вікі агент **обов'язково**:

1. Читає `chinazes/server.cfg` і будує список активних ensure
2. Перевіряє мапінг у **§9** цієї таблиці перед написанням сторінки
3. Ігнорує ресурси з `[dontEnsure]`, `[nedoroblene]` і закоментовані ensure
4. Для кожної теми вказує собі (внутрішньо) файл-джерело config
5. Перевіряє `[glovo]` / `[unit]` на override клавіш і UX
6. Не змінює захищені сторінки без явного запиту
7. Player-facing текст — українською, без назв ресурсів

---

*Оновлюй цей документ, якщо змінюється `server.cfg` (новий ensure, `stop`, закоментований старий, exec `unit.cfg` тощо) — особливо таблиці в §9 і snapshot у §10.*
