# SpiderMan
The objective of this program is to provide a safe website spider program.

The idea is to have this information reside in the terminal. Future enhancements may include visuals, but the goal is to have this Python3 native.

## Steps to run
1. If it does not exist, create the directory 'data/' in the project's root folder.
2. Run 'walkman.js' inside of the webpage you are currently in.
3. Right-click the results and click on 'Copy object'
4. Save the results as 'input.txt'
5. Run this program, which grabs the information from 'input.txt'

Please not that this program keeps a running set() of directories spidered.
If the directory appears in the set(), then it will not be included in other objects.

For example, if "/" contains "/test" and "/test2" as children, and "/test" has the child of "/test2" - "/test2" will not be created as a child directory of "/test2." This is important to note for hierarchical structures. Make sure you populate your most important hierarchies first.
