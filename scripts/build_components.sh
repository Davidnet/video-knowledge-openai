#!/bin/bash
set -e

poetry shell
kfp component build components/create_knowledge_db/ --component-filepattern "*.py"
kfp component build components/process_videos/ --component-filepattern "*.py"