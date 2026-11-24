"""
quiz.py - the daily quiz: 5 questions a day about diabetes.

The quiz is for the PARENT or guardian (the app is looked after by
adults), so the questions go deeper than "sugar is sweet". They are
mostly facts about how diabetes works, with few statistics.
Each one has 4 choices, the right answer, a short explanation and the
source it comes from.

>>> FOR THE TEAM TO REVIEW. Please check every question against its
source before the pitch. The full source list is in docs/flow.md. <<<

The quiz teaches general facts. It is not a diagnosis and not advice
for any person.

Every day 5 questions are picked from the list below. The pick depends
only on the date, so everyone gets the same 5 on the same day, and the
quiz can be closed and continued later.

Each question is a dict:
    id        a short name, never change it once used
    q         the question
    options   4 choices
    answer    the position of the right choice (0 = first)
    why       the explanation shown after answering
    source    short name of the source (see SOURCES)
"""

import random

import state_store

QUESTIONS_PER_DAY = 5
POINTS_PER_RIGHT_ANSWER = 5

SOURCES = {
    "WHO 2006": "WHO/IDF. Definition and diagnosis of diabetes mellitus "
                "and intermediate hyperglycaemia. 2006.",
    "WHO fact sheet": "World Health Organization. Diabetes fact sheet.",
    "WHO sugars 2015": "WHO. Guideline: sugars intake for adults and "
                       "children. 2015.",
    "WHO activity 2020": "WHO guidelines on physical activity and "
                         "sedentary behaviour. 2020.",
    "ADA Standards": "American Diabetes Association. Standards of Care "
                     "in Diabetes.",
    "GI tables 2008": "Atkinson FS, Foster-Powell K, Brand-Miller JC. "
                      "International tables of glycemic index and "
                      "glycemic load values. Diabetes Care. 2008;31:"
                      "2281-2283.",
    "Physiology": "Standard physiology textbooks (renal threshold for "
                  "glucose).",
}

QUESTIONS = [
    {"id": "fasting_cutoff",
     "q": "Under WHO criteria, which fasting plasma glucose level is in "
          "the diabetes range?",
     "options": ["5.6 mmol/L or more", "6.1 mmol/L or more",
                 "7.0 mmol/L or more", "11.1 mmol/L or more"],
     "answer": 2,
     "why": "WHO uses a fasting level of 7.0 mmol/L or more. 11.1 mmol/L "
            "is the level for the test 2 hours after a glucose drink. "
            "Only a doctor can confirm diabetes, usually with a repeat "
            "test.",
     "source": "WHO 2006"},
    {"id": "ifg_range",
     "q": "WHO calls a fasting plasma glucose that is above normal but "
          "below the diabetes range 'impaired fasting glucose'. What is "
          "that range?",
     "options": ["4.0 to 5.5 mmol/L", "6.1 to 6.9 mmol/L",
                 "7.0 to 11.0 mmol/L", "Above 11.1 mmol/L"],
     "answer": 1,
     "why": "WHO: 6.1 to 6.9 mmol/L. The American Diabetes Association "
            "starts lower, at 5.6 mmol/L. People in this range have a "
            "higher risk of type 2 diabetes later.",
     "source": "WHO 2006"},
    {"id": "hba1c_period",
     "q": "An HbA1c blood test reflects the average blood glucose over "
          "about how long?",
     "options": ["The last 24 hours", "The last week",
                 "The last 2 to 3 months", "The last 2 years"],
     "answer": 2,
     "why": "Glucose sticks to haemoglobin in red blood cells, and red "
            "blood cells live for about 3 to 4 months. So HbA1c shows "
            "the average of roughly the last 2 to 3 months.",
     "source": "ADA Standards"},
    {"id": "type1_cause",
     "q": "What goes wrong in type 1 diabetes?",
     "options": ["The body's cells stop responding to insulin",
                 "The immune system destroys the cells that make insulin",
                 "The liver stops storing glucose",
                 "The kidneys remove too much insulin"],
     "answer": 1,
     "why": "In type 1 diabetes the immune system destroys the beta "
            "cells in the pancreas, so the body makes little or no "
            "insulin. It is not caused by diet or lifestyle.",
     "source": "ADA Standards"},
    {"id": "insulin_resistance",
     "q": "In type 2 diabetes, what does 'insulin resistance' mean?",
     "options": ["The pancreas makes no insulin at all",
                 "Insulin is destroyed in the stomach",
                 "The body's cells respond poorly to insulin",
                 "The body becomes allergic to insulin injections"],
     "answer": 2,
     "why": "Muscle, fat and liver cells respond poorly to insulin, so "
            "glucose stays in the blood. The pancreas makes more insulin "
            "to keep up, and over time it may not make enough.",
     "source": "WHO fact sheet"},
    {"id": "beta_cells",
     "q": "Which cells make insulin?",
     "options": ["Alpha cells in the pancreas", "Beta cells in the pancreas",
                 "Red blood cells", "Cells in the liver"],
     "answer": 1,
     "why": "Beta cells in the islets of the pancreas make insulin, "
            "which lowers blood glucose. Alpha cells make glucagon, "
            "which raises it.",
     "source": "ADA Standards"},
    {"id": "kids_type",
     "q": "Which type of diabetes is the most common in children?",
     "options": ["Type 1 diabetes", "Type 2 diabetes",
                 "Gestational diabetes", "They are all equally common"],
     "answer": 0,
     "why": "Most children with diabetes have type 1. Type 2 is far more "
            "common in adults, although it is now also seen in children "
            "and teenagers.",
     "source": "ADA Standards"},
    {"id": "type1_prevent",
     "q": "Can type 1 diabetes be prevented by eating less sugar?",
     "options": ["Yes, sugar is its main cause",
                 "Yes, but only before the age of 5",
                 "No. Its cause is not fully known and it cannot be "
                 "prevented today",
                 "No, but exercise prevents it"],
     "answer": 2,
     "why": "WHO says that neither the cause of type 1 diabetes nor a "
            "way to prevent it is known. It is not caused by eating "
            "sweets, and it is nobody's fault.",
     "source": "WHO fact sheet"},
    {"id": "child_signs",
     "q": "Which group of signs are typical symptoms of diabetes?",
     "options": ["Very thirsty, passing urine often, tired, losing weight",
                 "Sneezing, itchy eyes and a runny nose",
                 "A sore throat and a cough",
                 "Growing taller quickly"],
     "answer": 0,
     "why": "WHO lists feeling very thirsty, needing to urinate more "
            "often than usual, tiredness, blurred vision and losing "
            "weight without trying. In type 1 diabetes they can appear "
            "suddenly.",
     "source": "WHO fact sheet"},
    {"id": "insulin_job",
     "q": "What does insulin do in the body?",
     "options": ["It breaks down fat in the stomach",
                 "It lets glucose move from the blood into the body's "
                 "cells",
                 "It makes the kidneys produce more urine",
                 "It carries oxygen in the blood"],
     "answer": 1,
     "why": "Insulin is a hormone that works like a key: it lets glucose "
            "leave the blood and enter the cells, where it is used for "
            "energy.",
     "source": "WHO fact sheet"},
    {"id": "gestational",
     "q": "A woman has gestational diabetes during pregnancy. How does "
          "it affect her chance of type 2 diabetes later in life?",
     "options": ["It is lower than for other women",
                 "It is the same as for other women",
                 "It is higher than for other women",
                 "It is higher only if the baby was large"],
     "answer": 2,
     "why": "Gestational diabetes usually goes away after the birth, but "
            "the mother (and possibly the child) has a higher risk of "
            "type 2 diabetes in the future.",
     "source": "WHO fact sheet"},
    {"id": "hypo_level",
     "q": "For people with diabetes, hypoglycaemia (low blood glucose) "
          "is usually defined as a level below what?",
     "options": ["7.0 mmol/L", "5.6 mmol/L", "3.9 mmol/L", "1.0 mmol/L"],
     "answer": 2,
     "why": "The American Diabetes Association defines level 1 "
            "hypoglycaemia as below 3.9 mmol/L (70 mg/dL), and level 2 "
            "as below 3.0 mmol/L.",
     "source": "ADA Standards"},
    {"id": "dka",
     "q": "What causes diabetic ketoacidosis (DKA)?",
     "options": ["Too much insulin, so glucose drops too low",
                 "Too little insulin, so the body burns fat and makes "
                 "ketones",
                 "Eating too much protein",
                 "Drinking too much water"],
     "answer": 1,
     "why": "With too little insulin the body cannot use glucose, so it "
            "burns fat instead. That makes ketones, which turn the blood "
            "acidic. DKA is an emergency and is most common in type 1 "
            "diabetes.",
     "source": "ADA Standards"},
    {"id": "glycaemic_index",
     "q": "What does the glycaemic index (GI) of a food tell you?",
     "options": ["How many calories it has",
                 "How much sugar is listed on the label",
                 "How fast its carbohydrate raises blood glucose, "
                 "compared with pure glucose",
                 "How much insulin the food contains"],
     "answer": 2,
     "why": "GI ranks carbohydrate foods from 0 to 100 by how fast they "
            "raise blood glucose, with pure glucose as 100. It does not "
            "measure calories or the amount eaten.",
     "source": "GI tables 2008"},
    {"id": "retinopathy",
     "q": "Diabetic retinopathy is damage to which part of the eye?",
     "options": ["The lens", "The cornea",
                 "The small blood vessels of the retina", "The eyelid"],
     "answer": 2,
     "why": "Long-term high blood glucose damages the small blood "
            "vessels in the retina at the back of the eye. It is an "
            "important cause of blindness.",
     "source": "WHO fact sheet"},
    {"id": "polyuria",
     "q": "Why does very high blood glucose cause frequent urination?",
     "options": ["The bladder becomes smaller",
                 "Glucose spills into the urine and pulls water with it",
                 "The kidneys stop filtering blood",
                 "Insulin makes people thirsty"],
     "answer": 1,
     "why": "Above roughly 10 mmol/L the kidneys cannot take all the "
            "glucose back into the blood. The glucose in the urine pulls "
            "water with it, which also causes thirst.",
     "source": "Physiology"},
    {"id": "who_sugar",
     "q": "WHO recommends keeping 'free sugars' below what share of the "
          "energy eaten in a day?",
     "options": ["Below 10%", "Below 25%", "Below 40%", "Below 50%"],
     "answer": 0,
     "why": "WHO recommends less than 10% of daily energy from free "
            "sugars, and says below 5% (about 25 grams, or 6 teaspoons) "
            "would give more benefit. Free sugars include sugar in "
            "drinks, honey and fruit juice.",
     "source": "WHO sugars 2015"},
    {"id": "kids_activity",
     "q": "How much activity a day does WHO recommend for children and "
          "teenagers aged 5 to 17?",
     "options": ["About 10 minutes", "About 30 minutes",
                 "At least 60 minutes on average", "At least 3 hours"],
     "answer": 2,
     "why": "WHO recommends an average of at least 60 minutes a day of "
            "moderate to vigorous activity for ages 5 to 17, such as "
            "running, cycling or active play.",
     "source": "WHO activity 2020"},
    {"id": "albumin",
     "q": "Which of these is an early sign of kidney damage from "
          "diabetes?",
     "options": ["Small amounts of the protein albumin in the urine",
                 "Darker hair", "A lower heart rate", "Better eyesight"],
     "answer": 0,
     "why": "Damaged kidney filters start to leak small amounts of "
            "albumin into the urine. That is why people with diabetes "
            "are offered a regular urine test.",
     "source": "ADA Standards"},
]


def questions_for(date_text):
    """The 5 questions of one day. The same date always gives the same 5."""
    picker = random.Random("quiz-" + date_text)
    return picker.sample(QUESTIONS, QUESTIONS_PER_DAY)


def todays_answers(state):
    """Today's answers so far (an older day's answers do not count)."""
    quiz = state["quiz"]
    if quiz["date"] != state_store.today_text():
        return []
    return quiz["answers"]


def answer(question_id, pick):
    """
    Save the answer to today's next question and give the points.
    Returns True if it was right.
    """
    today = state_store.today_text()
    questions = questions_for(today)
    result = {"correct": False}

    def change(state):
        quiz = state["quiz"]
        if quiz["date"] != today:            # a new day: start again
            quiz["date"] = today
            quiz["answers"] = []
        done = len(quiz["answers"])
        if done >= len(questions) or questions[done]["id"] != question_id:
            return                           # already answered: do nothing
        correct = (pick == questions[done]["answer"])
        quiz["answers"].append({"id": question_id, "pick": pick,
                                "correct": correct})
        if correct:
            state_store.add_points(state, POINTS_PER_RIGHT_ANSWER)
        result["correct"] = correct
    state_store.update_state(change)
    return result["correct"]
