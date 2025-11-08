# CheatSheet PRD
## Introduction

## Basic

## Basic Functionality(for MVP)
### Part 1 input & upload
1. A web page for uploading PDF files, with an OpenRouter API call that can process the file and generate a list of concepts (json format).
   1. Openrouter:
      1. model: gpt5
      2. how? see the openrouter.md
      3. api_key: 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
   2. the output format
        [
            {
                "title": "title of the concept",
                "content": "description of the concept"
            },
            {
                "title": "title of the concept",
                "content": "description of the concept"
            },
            ...
        ]
2. Process the output and add it to `db.json`
   1. a pop-up window list the `course`s from the `db.json`
      1. allow the user to select which `course` these concept points belong to, or let them add a new course to contain them.
      2. read the concepts in that course and remove any duplicate points. (不确定怎么做)
      3. process the output and add concept points to `db.json`
        e.g.: 
        "COURSES": {
            "SOFTWARE_CONSTRUCTION": {
                "sc-2025-01-11-001": {
                    "title": "Software Construction Overview",
                    "content": [
                    "The course focuses on principles related to objects, design, and concurrency in software construction. It includes assignments, exams, and collaborative learning activities."
                    ],
                    "timestamp": "2025-01-11T00:00:00Z",
                    "freshness": 0.18
                },
                ...
            }
        }
      4. use function `distributeData(USER_PROFILE)` update `data\knowledge_distrubuted_map.json`
         Purpose: Update `knowledge_distributed_map.json` after new insertions (auto-routing to TODAY, optionally SHORT_TERM/LONG_TERM accodring to `USER_PROFILE` in `db.json`, what user Long term need to care about).
    2. 进入Loading screen 
       1. 去掉目前的“Drop any files...”的区域下面的 “processing” 以及 “Key Concepts”区域
       2. 在处理的过程中在屏幕中心极简得显示每一步在做什么，包括：
          1. "Parsing the file..."
          2. "Generating the key points..."
          3. "Generated <num> key points."
          4. show 3 key points
          5. "Storing to the base"
          6. "Generating quizzes"
          7. "Generated <num> quizzes."
          8. a button: "Start quiz"

### Part 2 databaseSearch & init learn:
2. Prepare data to generate quizzes/learning session:
   1. use function `databaseSearch()` Retrieve actual reference set for generation/quiz based on user intent. Default user intent is "Learn this course according to the material." Output the reference data to generate quiz as next step.
   output:
      ```
         {
         "actual_reference_db":[
            "courses/SOFTWARE_CONSTRUCTION/sc-2025-08-11-001",
            "courses/SOFTWARE_CONSTRUCTION/sc-2025-01-11-003"
         ],
         "explanation":"Selected TODAY + LONG_TERM matches with 'concurrency' and 'decorator'."
         }
      ```
   2. `getCurProgress()` generate cur_progress.json  for runtime db
3. Generate and display quizzes
   1. For each concept point, generate a piece of quiz
      1. there are 3 kinds of quizzes, can be 3 different *TOOL*s:
         1. single choice
         2. multiple choice
         3. short answer
      2. write the quizzes in a temporary json file(或者其他合理格式的file?)
      3. the agent should make the decision of using which type/TOOL
      4. 进入 quiz screen  
   **code logic here:**
      1. user `getSystemPrompt()` to ground user, generate based on:
      ```
      {
      "TODAY": "Resolve refs from data/knowledge_distributed_map.json[\"TODAY\"] and fetch actual entries from db.json",
      "LONG_TERM": "Resolve refs from data/knowledge_distributed_map.json[\"LONG_TERM\"] and fetch actual entries from db.json",
      "SHORT_TERM": "Resolve refs from data/knowledge_distributed_map.json[\"SHORT_TERM\"] and fetch actual entries from db.json",
      "USER_PROFILE": "db.json#/user_profile"
      }
      ```
      2. use `getCurProgress()` to get the `cur_progress.json`, call `evaluateAnswer()` and `updateFreshnessAndLog()` to eval quiz ans and update freshness and log in `cur_progress.json`, then call `decideNext()`
      - `decideNext()`: Tutor policy—choose next step: another quiz vs summary.
         ```
         {
         "decision":"generateQue_singleChoice()|generateQue_multiChoice()|generateQue_shortAnswer()|generateExplaination",
         "reason":"low score on concurrency; retry with short-answer to test articulation",
         "target_ref":"courses/SOFTWARE_CONSTRUCTION/sc-2025-08-11-001",
         "preferred_quiz_type":"short_answer"
         }```
      - `generateExplaination()`: Produce a detail explain recap for the user
      - `generateQue_singleChoice()`: Purpose: Create a single-choice quiz per concept.
      - `generateQue_multiChoice()`: (similar shape; answer_indices:[...])
      - `generateQue_shortAnswer()`: create short answer quiz per concept.

4. For each quiz: user quiz interaction
   1. let the user answer the quiz
   2. *TOOL*s: 
      1. evaluate `user_answer`, either it's good or bad:
      2. update the point's `freshness_score`
      3. add an entry in the point's `log` (e.g.: Not familiar with ..., wrong concept of ...; or the user )
   3. use `getCurProgress()` to get the `cur_progress.json`, call `evaluateAnswer()` and `updateFreshnessAndLog()` to eval quiz ans and update freshness and log in `cur_progress.json`, then call `decideNext()`, and repeat the loop.

5. Endpoint: until the quiz_cnt >= 20, Quit learn session.


### Minimal userflow wiring
Upload → inputParse → concepts
Choose course → deduplicateConcepts → add2Data
Distribute → distributeData
Plan → databaseSearch → getCurProgress
Loop
- decideNext → generateQue_* or generateExplaination
- user answers → evaluateAnswer → updateFreshnessAndLog → updateMainDB
- repeat until don

## UI
### Style
minimalism
light mode

### Screens(Pages)
1. File drop screen
   1. a file drop area
   2. instruction "Drop any files"
2. Loading screen
   1. Left-align a continuously updating to-do list at the center of the screen.  
   2. Each item should be preceded by a solid small circle.  
   3. Completed items should appear grayed out and struck through.  
   4. Ongoing items should remain in black.
   5. the items include:
      1. "Parsing the file..."
      2. "Generating the key points..."
      3. "Generated <num> key points."
      4. show 3 key points
      5. "Storing to the base"
      6. "Generating quizzes"
      7.  "Generated <num> quizzes."
      8.  a button: "Start quiz"
3. Quiz screen
   1. one quiz at a time
   