from .core_components import ExecuteConfig
from .prog_langs import ProgLang

default_execute_config: dict[ProgLang, ExecuteConfig] = {
    "python": ExecuteConfig(source_filename="test.py", run="python test.py"),
    "java": ExecuteConfig(source_filename="Test.java", run="java Test.java"),
    "c": ExecuteConfig(
        source_filename="test.c", build="gcc test.c -o test", run="./test"
    ),
}

default_solution: dict[ProgLang, str] = {
    "python": "\n",
    "c": "\nint main(){}\n",
    "java": "\npublic class Main{public static void main(String[] args) {}}\n",
}
