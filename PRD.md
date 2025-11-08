# CheatSheet PRD
## Introduction

## Basic

## Basic Functionality(for MVP)
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
3. Generate and display quizzes
   1. For each concept point, generate a piece of quiz
      1. there are 3 kinds of quizzes, can be 3 different *TOOL*s:
         1. single choice
         2. multiple choice
         3. short answer
      2. write the quizzes in a temporary json file(或者其他合理格式的file?)
      3. the agent should make the decision of using which type/TOOL
      4. 进入 quiz screen
4. For each quiz: user quiz interaction
   1. let the user answer the quiz
   2. *TOOL*s: 
      1. evaluate `user_answer`, either it's good or bad:
      2. update the point's `freshness_score`
      3. add an entry in the point's `log` (e.g.: Not familiar with ..., wrong concept of ...; or the user )
      4. 

### MCP tool list:   `
1. `distributeData(new input data in structure) -> return knowledge_distributed_map`
description: When new data is input into the system, append and update db.json,  knowledge_distributed_map.

2. `databaseSearch(input_prompt, db.json, knowledge_distributed_map) -> return actual_reference_db_to_gen_next`
   imp_base = ALL_COURSE.find according "FOUNDATION/LONG_TERM"
   partial_related = ALL_COURSE.find according "SHORT_TERM/THIS_SEM"
   today = ALL_COURSE.find according “TODAY”  # focus this on generate
   actual_reference_db_to_gen_next = modal( "FOUNDATION/LONG_TERM", input_prompt)  # based on foundation/LONG_TERM, decide what else in databse is related, give back id in ALL_COURSE
   return actual_reference_db_to_gen_next

3. decideNext()

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
   