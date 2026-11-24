# How the prototype flows

This is a **prototype**. The keychain is simulated in a desktop window
because we have no hardware. Both apps say so on screen.

## The big idea

- **Made for kids aged 6 to 14, with their parents.** The kid plays
  with the keychain. A parent or guardian looks after the companion app
  (linking, insulin times, vouchers) together with the kid.
- The problem we work on is **education and awareness**: learning early
  how everyday food choices relate to blood sugar, and helping kids who
  take insulin keep to their times.
- **Learning by playing.** The keychain is a little companion called Suggy.
  Looking after Suggy teaches small facts about food, sugar and moving more.
- **Four features for now:** **feeding** Suggy, the **insulin
  reminder** (for kids who take insulin), **checking** on Suggy and a
  short **quiz** for kids.
  Step tracking was removed: kids can shake the device, which would
  make the step numbers wrong.
- **Works with no phone and no app.** Everything is on the keychain.
- **The companion app** links to the keychain with a nickname, an
  **IC number** and the keychain's **reference number**. It keeps the
  feeding data and the insulin reminder times, and it has **points** and
  a **shop**.
- **Points.** +10 for each light food choice, +5 for each right quiz
  answer. Points buy cosmetics for Suggy in the app's shop, and a bought
  cosmetic shows on the app **and** on the keychain.

## Keychain window (`keychain/`)

**Smooth turning:** while you drag, the keychain follows the mouse at a
steady 60 frames a second and glides to a stop when you let go. Turns
are timed by the clock, so a slow computer skips frames instead of
slowing down. The buttons light up under the mouse.

**Look:** the window shows a **3D model of the keychain**, built to follow
the team's concept picture: a plush kidney character with a face, little
arms, a glucose meter in one hand, a stethoscope, three coloured tubes on
its side, a strap with a gold ring, and on the back a cream frame with the
screen and three buttons, speaker holes, and a charging port underneath.

- **Drag it with the mouse** to turn it and see every side.
- **Turn around** (button under the keychain) spins between face and back.
- It opens on the face, then spins to the **back**. Let go near the back
  and it settles there.
- The live screen only works when the keychain is settled on its back.
  Pressing A, B or Back while it is turned spins it to the back first.

How it is made: `keychain/keychain_model.py` builds the shape from simple
pieces (balls, tubes, blocks, plates). `keychain/keychain_frame.py` is a
small 3D viewer written with only Tkinter. To stay smooth it draws a
light version of the model while you turn it and the detailed version
when you stop. No extra libraries. (Fur cannot be drawn this way, so the
model is smooth.)

**Buttons.** The same jobs on every page:

| Button | Job | Keyboard |
|---|---|---|
| **Left arrow** | move to the choice on the left | Left arrow key |
| **OK** | pick the choice / carry on | Enter or Space |
| **Right arrow** | move to the choice on the right | Right arrow key |
| **Home** (small, above the screen) | back to the hello page, from anywhere | H or Esc |

Pressing Home in the middle of a feeding leaves it. An unfinished
feeding is not saved.

**Text.** Few words on each page. A dark box at the bottom says what OK
does on that page, for example `OK: start`.

The reference number is printed near the bottom of the
keychain body. Outside the keychain frame there is a demo-only button:
**Insulin reminder now** (shows the reminder without waiting for its time).

The keychain re-reads `data/state.json` every second, so changes from the
app show up by themselves.

### 1. Hello page

- Not linked: "Hello! I'm Suggy".
- Linked: "Hello <nickname>!" (the nickname typed in the app).
- Suggy is drawn as a little **kidney**, like the keychain itself.
- OK = start (go to the menu).

### 2. Menu

Four cards, two on top and two below: **Feed**, **Insulin**, **Check**
and **Quiz**. The arrows
move the thick border, OK opens that one.

### 3. Feed Suggy

- Suggy can be fed **at any time**, as often as the player likes. There
  are no meal times.
- Every feeding goes **step by step**: meal, then drink, then dessert.
  Each step is a choice between **two** very different foods shown side
  by side, a sweet one and a light one.
- There are three pairs for each step, and every feeding picks one pair
  at random, so the foods change each time. The light food is not always
  on the same side.

  | Step | Sweet choice | Light choice |
  |---|---|---|
  | Meal | White rice | Brown rice |
  | Meal | White bread | Wholemeal bread |
  | Meal | Sweet cereal | Oats |
  | Drink | Sweet drink | Water |
  | Drink | Fruit juice | Plain tea |
  | Drink | Bubble tea | Plain milk |
  | Dessert | Ice cream | Apple |
  | Dessert | Donut | Banana |
  | Dessert | Sweet cake | Plain nuts |

- The arrows move between the two foods. Under the cards is a **short
  description** of the chosen food in **words for kids**, for example
  "Turns to sugar fast." or "Slow, steady energy." OK feeds it to Suggy.
- After the three steps, Suggy's **pretend** sugar level is shown (a game
  number, not anyone's real glucose). Suggy has 5 hearts: two or three
  sweet choices (pretend sugar 8.0 or more) take one heart, lighter
  feedings give one back. At 0 hearts Suggy is very tired and **falls
  asleep**. OK wakes Suggy up with all the hearts back. Nothing is lost:
  the cosmetics and the points stay.
- **Points.** Each light choice gives +10 points (up to +30 in one
  feeding). The result page shows them, for example "+1 heart +20 pts".
- **Suggy's smile fades with sugar.** On the result page Suggy smiles if
  no sweet food was picked, has a flat mouth for one sweet pick, and a
  little frown for two or three. No words of blame are shown.
- To add a pair, edit `FOOD_PAIRS` in `keychain/feeding.py` and add a
  picture in `keychain/pet_drawing.py`.

#### Why the food words are simple

The players are kids, and some of them have diabetes themselves. So the
cards use no numbers, no "risk", and nothing that says a food gives
anyone diabetes (type 1 diabetes is not caused by food). They only say
simple things about the food: how much sugar it has, and whether its
energy comes fast or slowly. The earlier version showed percentages
from studies of adults (Sun 2010, Malik 2010, Muraki 2013). Those were
removed.

### 4. Insulin reminder

For kids who take insulin. Every kid's plan is different, so **a parent
sets the times in the app, copied from the doctor's plan**. Nothing is
fixed in the code.

- **No dose anywhere.** The keychain reminds about the **time** only. It
  never says how much insulin to take and gives no advice.
- When a reminder time comes, **"Insulin time!"** pops up by itself (with
  a little sound) and shows which one it is, for example "Lunch 12:30".
  OK = took it. The time of the press is saved.
- If that insulin goes with a meal, the next page counts down:
  **"Eat in 15 min"**, then **"Time to eat!"**. OK = I ate. That time is
  saved too. The wait (15 minutes to start with) is set in the app.
- A bedtime reminder has no meal after it, so it goes straight to
  "Saved!".
- The small Home button hides a reminder for 5 minutes, then it comes
  back. A reminder stops asking 2 hours after its time. It never pops up
  in the middle of a feeding.
- The **Insulin** card in the menu shows today's times with a tick on
  the ones that are done.
- **No points** are given for pressing OK, so nobody is tempted to press
  it without taking the insulin.
- Demo: the **Insulin reminder now** button under the keychain shows a
  reminder straight away. Its rows are marked "demo" in the app.

### 5. Check on Suggy

- This page shows how Suggy is doing, in a gentle way.
- For every heart Suggy has lost, one more body part looks **tired** (a
  soft pale patch), in this order. These are the parts doctors look
  after in people with diabetes. The fact under each part is kind and
  simple and says what steady sugar **helps**, for example "Steady
  sugar helps eyes see clearly."

  | Hearts left | Tired parts |
  |---|---|
  | 5 | none |
  | 4 | eyes |
  | 3 | eyes, hands |
  | 2 | eyes, hands, legs |
  | 1 | eyes, hands, legs, kidney |

- The marks also show on Suggy on the hello page and after a feeding.
  They go away again as hearts come back.
- The arrows move through the four parts. A short fact about the chosen
  part is shown, for example "Years of high sugar can damage the eyes
  and harm eyesight." These are general health facts (long-term high
  blood sugar can damage small blood vessels and nerves). They are not
  a diagnosis and not advice. The list is `BODY_PARTS` in
  `keychain/feeding.py`.
- OK = back to the menu.

### 6. Quiz (for kids)

A short quiz for kids aged 6 to 14. It is separate from the harder
parent quiz in the app.

- One round is **3 questions**, picked at random from 12 in
  `keychain/kid_quiz.py`.
- Every question has **two answers** on two cards. The arrows move
  between them, OK picks one.
- After each pick: "Yes!" or "Not quite" and one short fact. No blame.
- At the end: "2 of 3 right!" and the points earned.
- **Points:** +5 for each right answer, for the **first round of the day
  only** (up to +15 a day). Playing again is allowed but gives no more
  points until tomorrow, so points cannot be collected by repeating it.
- **For the team to review:** please read the 12 questions before the
  pitch.

| Question | Right answer | Other answer |
|---|---|---|
| Which drink has no sugar? | Water | Soft drink |
| Which gives slow, steady energy? | Brown rice | Sweets |
| What does your body use sugar for? | Energy | Sleep |
| What helps sugar get into your cells? | Insulin | Water |
| Can you catch diabetes? | No | Yes |
| Which has more fibre? | Apple | Apple juice |
| Where is insulin made? | Pancreas | Heart |
| Is active play good for you? | Yes | No |
| Which has lots of added sugar? | Bubble tea | Plain milk |
| How many kidneys do most people have? | Two | Five |
| Do sweets cause type 1 diabetes? | No | Yes |
| Who helps people with diabetes? | Doctors | Pirates |

## Companion app (`adult-app/`)

The folder is called `adult-app` because an adult (a parent or guardian)
looks after it. The window says "For a parent or guardian, together with
their child".

### The look and the animations

All of this is plain Tkinter, in `adult-app/fun.py`:

- **Warm theme**: cream background, orange buttons like the keychain's,
  bigger tabs. Buttons light up when the mouse is over them.
- **Banner** at the top: Suggy bobbing (wearing its cosmetics), the
  title, and the points with a star. Click Suggy and it jumps.
- **Numbers count up** when points change (banner, Home, Shop,
  Vouchers), instead of jumping.
- **Celebration card** with falling confetti and a jumping Suggy, for
  about 2 seconds: when points are earned ("+10 points!"), an item is
  bought ("New look!"), a voucher is claimed, or the keychain is linked.
  A click closes it early.

### 1. Link your keychain (always first)

- Type a nickname (max 8 letters), an IC number and the keychain
  reference number, then **Link keychain**.
- Checks: the IC must be 12 digits and start with a real birth date
  (YYMMDD). The reference number must match the keychain.
- **Privacy (PDPA):** the app only checks that the IC looks real and
  saves **nothing** from it (no age group either). The IC number
  is never saved and never sent anywhere. The IC box is cleared after
  linking. On screen: "Demo: use a made-up IC".
- The keychain's Welcome page then says "Hello <nickname>!".
- **Unlink (demo)** removes the link so the demo can be shown again.

### 2. After linking: the tabs

Before linking only the **Link** tab can be opened. Linking opens the
others. Everything updates by itself about once a second.

- **Home**: "Hello <nickname>!", the points balance, a picture of Suggy
  (the same drawing as on the keychain, with cosmetics, hearts and tired
  marks), the insulin reminder times and the number of saved feedings.
- **Feeding**: every feeding done on the keychain, newest first: the
  time, the meal, drink and dessert picked, and the points it gave.
  Under the list: how many light and sweet choices in total.
- **Insulin** (for a parent or guardian): four reminders that can be
  switched on, **Breakfast, Lunch, Dinner** (each followed by a meal)
  and **Bedtime** (no meal). Type each time in 24-hour form, set the
  minutes between insulin and eating (0 to 30), and press **Save
  times**. Under it, a list of what the kid pressed on the keychain:
  the planned time, when the insulin was taken, when they ate, and the
  minutes in between. No dose is typed or shown anywhere.
- **Shop**: the points balance, Suggy as it looks now, and three
  categories: **Head**, **Eyes** and **Neck**, with 5 items each. Every
  item has a picture of Suggy wearing it, a price and one button:
  **Buy**, then **Wear** or **Take off** once it is owned. Suggy wears at
  most one item from each category. What Suggy wears shows here and on
  the keychain.
- **Vouchers**: exchange points for vouchers. See below.
- **Quiz**: 5 questions a day about diabetes. See below.

**The shop list is a placeholder.** The items and prices are not decided
yet. They are in one place, `SHOP` in `adult-app/shop.py`:

| Category | Items (placeholder price in points) |
|---|---|
| Head | Cap 20, Beanie 20, Hair bow 30, Top hat 40, Crown 60 |
| Eyes | Round glasses 20, Square glasses 20, Sunglasses 30, Monocle 40, Goggles 50 |
| Neck | Scarf 20, Bow tie 20, Necktie 30, Necklace 40, Medal 60 |

A new kind of item also needs a drawing in `pet_drawing.py`
(`draw_accessories`). That file has two identical copies, one in
`keychain/` and one in `adult-app/`.

### Vouchers (demo only)

Points can be exchanged for vouchers.

- **The main reward is seeing a doctor.** "Diabetes consultation with a
  doctor" and "Blood sugar screening" sit at the top of the tab in a
  highlighted yellow box.
- Under it are **price-off vouchers** in three groups, chosen with three
  buttons:
  - **Pharmacy**: for example money off insulin (with a doctor's
    prescription), test strips, lancets and pen needles.
  - **Equipment**: things people use every day, with items made for
    kids, such as a small simple glucose meter, a kids' medical ID
    bracelet and an insulin cooling pouch that fits a school bag.
  - **Food swaps**: the lighter food made cheaper than the sweet one,
    for example "RM5 off brown rice, instead of white rice". They match
    the food pairs on the keychain.
- Claiming takes the points away and shows a made-up code such as
  `DEMO-7KQ2-XM4P` under "My vouchers".
- The users are children aged 6 to 14, so the tab says a parent or
  guardian would use the voucher.

**Nothing here is real.** Vendors and prices are not confirmed, nothing
is booked and the codes cannot be used anywhere. The tab says so in red.
The list and costs are placeholders in `VOUCHERS` in
`adult-app/vouchers.py`:

| Group | Voucher | Note | Cost (placeholder) |
|---|---|---|---|
| Doctor consultation | Diabetes consultation with a doctor |  | 300 points |
| Doctor consultation | Blood sugar screening |  | 200 points |
| Pharmacy | RM10 off insulin | with a doctor's prescription | 150 points |
| Pharmacy | RM5 off glucose test strips |  | 80 points |
| Pharmacy | RM5 off lancets | finger-prick needles | 60 points |
| Pharmacy | RM5 off insulin pen needles |  | 60 points |
| Equipment | RM20 off a blood glucose meter | small, simple model for kids | 200 points |
| Equipment | RM10 off a medical ID bracelet | kids' sizes | 100 points |
| Equipment | RM10 off an insulin cooling pouch | fits a school bag | 100 points |
| Equipment | RM10 off a water bottle |  | 80 points |
| Equipment | RM10 off sports shoes |  | 150 points |
| Food swaps | RM5 off brown rice | instead of white rice | 100 points |
| Food swaps | RM3 off wholemeal bread | instead of white bread | 60 points |
| Food swaps | RM3 off oats | instead of sweet cereal | 60 points |
| Food swaps | RM2 off plain milk | instead of bubble tea | 40 points |
| Food swaps | RM3 off fresh fruit | instead of ice cream or cake | 60 points |

### Daily quiz

- The quiz is **for the parent or guardian**. It is mostly facts about
  how diabetes works, with few statistics.
- 5 questions a day, picked from a list of 19 in `adult-app/quiz.py`.
  The pick depends only on the date, so the same day always gives the
  same 5, and the quiz can be closed and continued later.
- One question at a time with 4 choices. After an answer the app marks
  the right choice and shows a short explanation and the source.
- A right answer gives **5 points** (up to 25 a day). A wrong answer
  shows "Not quite" with the explanation. No blame.
- The questions are general facts, not a diagnosis and not advice.

**For the team to review.** Please check every question and answer
against its source before the pitch. They were written from these
well-known sources but were not re-checked against the documents line
by line:

| # | Question | Right answer | Source |
|---|---|---|---|
| 1 | Under WHO criteria, which fasting plasma glucose level is in the diabetes range? | 7.0 mmol/L or more | WHO 2006 |
| 2 | WHO calls a fasting plasma glucose that is above normal but below the diabetes range 'impaired fasting glucose'. What is that range? | 6.1 to 6.9 mmol/L | WHO 2006 |
| 3 | An HbA1c blood test reflects the average blood glucose over about how long? | The last 2 to 3 months | ADA Standards |
| 4 | What goes wrong in type 1 diabetes? | The immune system destroys the cells that make insulin | ADA Standards |
| 5 | In type 2 diabetes, what does 'insulin resistance' mean? | The body's cells respond poorly to insulin | WHO fact sheet |
| 6 | Which cells make insulin? | Beta cells in the pancreas | ADA Standards |
| 7 | Which type of diabetes is the most common in children? | Type 1 diabetes | ADA Standards |
| 8 | Can type 1 diabetes be prevented by eating less sugar? | No. Its cause is not fully known and it cannot be prevented today | WHO fact sheet |
| 9 | Which group of signs are typical symptoms of diabetes? | Very thirsty, passing urine often, tired, losing weight | WHO fact sheet |
| 10 | What does insulin do in the body? | It lets glucose move from the blood into the body's cells | WHO fact sheet |
| 11 | A woman has gestational diabetes during pregnancy. How does it affect her chance of type 2 diabetes later in life? | It is higher than for other women | WHO fact sheet |
| 12 | For people with diabetes, hypoglycaemia (low blood glucose) is usually defined as a level below what? | 3.9 mmol/L | ADA Standards |
| 13 | What causes diabetic ketoacidosis (DKA)? | Too little insulin, so the body burns fat and makes ketones | ADA Standards |
| 14 | What does the glycaemic index (GI) of a food tell you? | How fast its carbohydrate raises blood glucose, compared with pure glucose | GI tables 2008 |
| 15 | Diabetic retinopathy is damage to which part of the eye? | The small blood vessels of the retina | WHO fact sheet |
| 16 | Why does very high blood glucose cause frequent urination? | Glucose spills into the urine and pulls water with it | Physiology |
| 17 | WHO recommends keeping 'free sugars' below what share of the energy eaten in a day? | Below 10% | WHO sugars 2015 |
| 18 | How much activity a day does WHO recommend for children and teenagers aged 5 to 17? | At least 60 minutes on average | WHO activity 2020 |
| 19 | Which of these is an early sign of kidney damage from diabetes? | Small amounts of the protein albumin in the urine | ADA Standards |

| Short name | Full source |
|---|---|
| WHO 2006 | WHO/IDF. Definition and diagnosis of diabetes mellitus and intermediate hyperglycaemia. 2006. |
| WHO fact sheet | World Health Organization. Diabetes fact sheet. |
| WHO sugars 2015 | WHO. Guideline: sugars intake for adults and children. 2015. |
| WHO activity 2020 | WHO guidelines on physical activity and sedentary behaviour. 2020. |
| ADA Standards | American Diabetes Association. Standards of Care in Diabetes. |
| GI tables 2008 | Atkinson FS, Foster-Powell K, Brand-Miller JC. International tables of glycemic index and glycemic load values. Diabetes Care. 2008;31:2281-2283. |
| Physiology | Standard physiology textbooks (renal threshold for glucose). |

### Points rules

| What | Points |
|---|---|
| Each light food choice in a feeding | +10 |
| Each right answer in the daily quiz (app, for parents) | +5 |
| Each right answer in the kids' quiz (keychain), first round of the day | +5 |

Cosmetics come only from the shop. Step tracking and its points were
removed. The insulin reminder gives no points on purpose.

## How the two apps talk

They share `data/state.json` (see `docs/data-format.md`). Each app re-reads
it about once per second. No network, no accounts, no server.

## Wording rules

Wellness language only. Never say the product "detects", "diagnoses",
"monitors glucose" or "prevents diabetes". No guilt or shame language.

## Milestones (updated)

1. Files, docs and the data helper (done)
2. Keychain window shell (done)
3. Age gate (done, later replaced by linking)
4. Adult menu (done, later replaced)
5. Pet and feeding (done)
6. Linking: IC + reference number in the app (done)
7. Welcome page, 3-feature menu, Steps with GPS demo and accessories,
   keychain glucose entry, more foods and life span (done)
8. 3D keychain model; few words and big text (done)
9. Focus at that time (later changed to kids 6 to 14): young adults 18 to 29, education and awareness. Keychain
   has Feed Suggy and Steps only (done)
10. Arrow buttons with OK; Suggy drawn as a kidney; feeding step by step
    (meal, drink, dessert) with two choices and a sourced description
    under each food (done)
11. Small Home button; feeding open at any time (meal times removed);
    three food pairs per step, picked at random; pet renamed Suggy (done)
12. Check on Suggy page with sore marks on eyes, hands, legs and kidney;
    Suggy's smile fades with sweet choices (done)
13. Companion app: Home, Feeding, Steps and Shop tabs; points for light
    choices and for 3,000 steps; cosmetics bought in the shop show on
    the app and the keychain (done, shop items and prices are placeholders)
14. Shop with 3 categories of 5 pictured items; demo vouchers; daily
    quiz of 5 questions (done, shop, vouchers and quiz need team review)
15. Vouchers: doctor consultation as the main reward, pharmacy and
    equipment price-off vouchers; target group changed to kids (now 6 to 14)
    (done)
16. Insulin reminder (times set by a parent in the app, no dose); step
    tracking removed (done)
17. Wording changed for kids (now 6 to 14) with parents; Link tab status
    removed (done)
18. Kid-friendly food words (study percentages removed); Suggy falls
    asleep instead of passing away; gentler Check page; parent quiz with
    more facts and fewer statistics; IC age group and step counter
    voucher removed (done)
19. Target age set to 6 to 14; kids' quiz on the keychain (done,
    questions need team review)
20. UI round: smoother 3D keychain; app theme, banner, count-up points
    and confetti celebrations (done)
21. Polish, wording review and README
