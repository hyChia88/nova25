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
      2. read the concepts in that course and remove any duplicate points.
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
3. Generate and display quizes
   1. For each concept point, generate a piece of quiz
      1. there are 3 kinds of quizes, can be 3 different *TOOL*s:
         1. single choice
         2. multiple choice
         3. short answer
      2. the agent should make the decision of using which type/TOOL
   2. 
4. For each quiz: user quiz interaction
   1. let the user answer the quiz
   2. *TOOL*s: 
      1. evaluate `user_answer`, either it's good or bad:
      2. update the point's `freshness_score`
      3. add an entry in the point's `log` (e.g.: Not familiar with ..., wrong concept of ...; or the user )
      4. 


## UI
### Style
minimalism
light mode

### Screens(Pages)
1. File drop screen
   1. a file drop area
   2. instruction "Drop any files"
2. Quiz screen
   1. one quiz at a time
   