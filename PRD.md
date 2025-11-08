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
    3. 将结果解析并写进`pdf2points_example.json`
2. 


## UI
### Style
minimalism
light mode

### Screens(Pages)
1. File drop screen
   1. a file drop area
   2. instruction "Drop any files"
2. 