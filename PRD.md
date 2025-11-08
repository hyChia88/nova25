# CheatSheet PRD
## Introduction

## Technical Architecture

### Framework & Stack
1. **Backend Framework**: FastMCP (Model Context Protocol)
   - Agent: Tool-calling agent with LLM integration
   - MCP Server: Custom `mcp_cheatsheet` server for education domain
   - LLM Provider: OpenRouter API (model: gpt-4o)
   
2. **Web Framework**: Flask
   - API endpoints for file upload
   - Server-Sent Events (SSE) for real-time loading screen updates
   - Static file serving for frontend

3. **Frontend**: HTML + JavaScript
   - Minimalist design
   - Three screens: File drop, Loading, Quiz

4. **Data Storage**: JSON files (in-memory database)
   - `db.json`: Main knowledge base
   - `knowledge_distributed_map.json`: Time-based distribution
   - `cur_progress.json`: Runtime session state

### Project Structure
/
├── python/
│ ├── agent/ # Tool-calling agent
│ │ ├── src/
│ │ │ └── agent/
│ │ │ ├── agent.py # Main agent loop
│ │ │ ├── tool_manager.py # MCP tool aggregation
│ │ │ ├── mcp_client.py # MCP protocol client
│ │ │ ├── config.py # LLM & rate limit config
│ │ │ ├── webui.py # Flask web server
│ │ │ ├── prompts/
│ │ │ │ └── system_prompt.txt
│ │ │ └── templates/
│ │ │ └── webui.html # Main UI (3 screens)
│ │ └── pyproject.toml
│ │
│ └── mcp_cheatsheet/ # Education domain MCP server
│ ├── src/
│ │ └── mcp_cheatsheet/
│ │ ├── server.py # FastMCP server factory
│ │ ├── database.py # JSON database manager
│ │ ├── tools.py # 11 MCP tools implementation
│ │ ├── models.py # Data models
│ │ └── app.py # HTTP server entry
│ └── pyproject.toml
│
├── data/
│ ├── db.json
│ ├── knowledge_distributed_map.json
│ ├── knowledge_distributed_map_example.json
│ ├── cur_progress.json
│ └── cur_progress_example.json
│
└── README.md

## Data
1. `db.json`
   1. "USER_PROFILE"
   2. "COURSES"
      1. 用来分course存储知识点
2. `knowledge_distributed_map.json`
   1. "TODAY": 今天新加入的知识点
   2. "LONG_TERM": 和“USER_PROFILE”相关的知识点（相对固定）
   3. "SHORT_TERM": 根据timestamp 找到 今年的知识点（和当前timestamp对比）
   4. format_example: `knowledge_distributed_map_example.json`
3. `cur_progress.json`
   1. 用来log user quiz interaction
      1. 每条quiz过的知识点：
         1. update freshness_score
         2. add a LLM-summarized log
   2. format_example: `cur_progress_example.json`


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
      4. use function `distributeData(USER_PROFILE)` update `data/knowledge_distributed_map.json`
         Purpose: Update `knowledge_distributed_map.json` after new insertions (auto-routing to TODAY, optionally SHORT_TERM/LONG_TERM according to `USER_PROFILE` in `db.json`, what user Long term need to care about).
    2. 进入Loading screen 
       1. 去掉目前的“Drop any files...”的区域下面的 “processing” 以及 “Key Concepts”区域
       2. 在处理的过程中在屏幕中心极简得显示每一步在做什么，包括：
       3. 我希望有更明显地区分正在进行（加载）的进程和已完成的进程
          1. "Parsing the file..."
          2. "Generating the key points..."
          3. "Generated <num> key points."
          4. show 3 key points（最下面显示省略号）
          5. "Storing to the base"
          6. "Distributing the points"
          7. "Generating quizzes"
          8. "Generated <num> quizzes."
          9. a button: "Start quiz"

### Part 2 databaseSearch & init learn:
**Note**: Part 2 runs in the backend while the Loading screen (Part 1, section 2.2) is displayed on the frontend. Each step updates the Loading screen progressively. When "Generating quizzes" completes, the "Start quiz" button appears.

1. Prepare data to generate quizzes/learning session:
   1. use function `databaseSearch()` Retrieve actual reference set for generation/quiz based on user intent. Default user intent is "Learn this course according to the material." Output the reference data to generate quiz as next step.
   output:
      ```
         [
            "courses/SOFTWARE_CONSTRUCTION/sc-2025-08-11-001",
            "courses/SOFTWARE_CONSTRUCTION/sc-2025-01-11-003"
         ]
      ```
   2. `getCurProgress()` generate cur_progress.json  for runtime db
2. Generate and display quizzes
   1. For each concept point, generate a piece of quiz, based on `cur_progress.json` + `knowledge_distributed_map.json`
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

3. For each quiz: user quiz interaction
   1. let the user answer the quiz
   2. *TOOL*s: 
      1. evaluate `user_answer`, either it's good or bad:
      2. update the point's `freshness_score` (in `cur_progress.json`)
      3. add an entry in the point's `log` (in `cur_progress.json`) (e.g.: Not familiar with ..., wrong concept of ...; or the user )

### MCP tool list:
1. `distributeData(USER_PROFILE) -> void`
   - **Purpose**: Rewrite `knowledge_distributed_map.json` after new concepts are inserted into db.json
   - **Input**: USER_PROFILE from db.json
   - **Function**: Auto-route new concepts to TODAY, and categorize existing concepts to SHORT_TERM/LONG_TERM according to USER_PROFILE and timestamp

2. `databaseSearch(input_prompt, db.json, knowledge_distributed_map) -> Array[string]`
   - **Purpose**: Retrieve actual reference set for generation/quiz based on user intent
   - **Input**: 
     - input_prompt: User's learning intent (default: "Learn this course according to the material")
     - db.json: Full database
     - knowledge_distributed_map: Distribution map
   - **Output**: Array of concept IDs (e.g., ["courses/SOFTWARE_CONSTRUCTION/sc-2025-08-11-001", ...])
   - **Logic**:
     - imp_base = ALL_COURSE.find according "FOUNDATION/LONG_TERM"
     - partial_related = ALL_COURSE.find according "SHORT_TERM/THIS_SEM"
     - today = ALL_COURSE.find according "TODAY"  # focus this on generate
     - actual_reference_db_to_gen_next = model("FOUNDATION/LONG_TERM", input_prompt)  # based on foundation/LONG_TERM, decide what else in database is related

3. `getCurProgress() -> cur_progress.json`
   - **Purpose**: Generate runtime database for current quiz session
   - **Output**: cur_progress.json with session state

4. `getSystemPrompt() -> string`
   - **Purpose**: Generate system prompt by resolving references from knowledge_distributed_map
   - **Returns**: System prompt with resolved TODAY, LONG_TERM, SHORT_TERM, and USER_PROFILE data

5. `evaluateAnswer(user_answer, correct_answer, concept_id) -> evaluation_result`
   - **Purpose**: Evaluate user's quiz answer
   - **Input**: user_answer, correct_answer, concept_id
   - **Output**: {score, feedback, is_correct}

6. `updateFreshnessAndLog(concept_id, evaluation_result) -> void`
   - **Purpose**: Update freshness score and log in cur_progress.json
   - **Input**: concept_id, evaluation_result
   - **Function**: Update the concept's freshness_score and append log entry

7. `decideNext(cur_progress) -> decision_object`
   - **Purpose**: Tutor policy—choose next step: another quiz vs summary
   - **Input**: cur_progress.json
   - **Output**: 
     ```json
     {
       "decision": "generateQue_singleChoice()|generateQue_multiChoice()|generateQue_shortAnswer()|generateExplaination",
       "reason": "low score on concurrency; retry with short-answer to test articulation",
       "target_ref": "courses/SOFTWARE_CONSTRUCTION/sc-2025-08-11-001",
       "preferred_quiz_type": "short_answer"
     }
     ```

8. `generateExplaination(concept_id) -> explanation_text`
   - **Purpose**: Produce a detailed explain recap for the user
   - **Input**: concept_id
   - **Output**: Formatted explanation text

9. `generateQue_singleChoice(concept_id) -> quiz_object`
   - **Purpose**: Create a single-choice quiz per concept
   - **Output**: 
     ```json
     {
       "question": "...",
       "options": ["A", "B", "C", "D"],
       "correct_answer": 0
     }
     ```

10. `generateQue_multiChoice(concept_id) -> quiz_object`
    - **Purpose**: Create a multiple-choice quiz per concept
    - **Output**: Similar to single choice, but answer_indices: [0, 2]

11. `generateQue_shortAnswer(concept_id) -> quiz_object`
    - **Purpose**: Create short answer quiz per concept
    - **Output**: 
      ```json
      {
        "question": "...",
        "expected_answer": "..."
      }
      ```

## UI
### Style
minimalism
light mode

### Screens(Pages)
1. File drop screen
   1. a file drop area
   2. instruction "Drop any files"
2. Loading screen
   1. See Part 1, section 2.2 for detailed loading screen specifications
3. Quiz screen
   1. one quiz at a time
   2. if there is a explanation generated
      1. display the explanation bellow.
      2. display a "I got it!" button
   