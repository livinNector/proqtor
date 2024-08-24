from pydantic import (
    BaseModel,
    Field,
    computed_field,
    TypeAdapter,
    field_validator,
)

from ..template_utils import relative_env
from md2json import dictify
import yaml
from .parse_utils import (
    remove_duplicate_whitespace,
    extract_codeblock_content,
)

from .proq import ProQ, Solution


class ProQSet(BaseModel):
    name: str
    proqs: list[ProQ]

    _normalize_name = field_validator("name")(remove_duplicate_whitespace)




class YamlConfig(BaseModel):
    solution_config: dict = Field(default_factory=dict)
    proq_config: dict = Field(default_factory=dict)


class ProQSets(BaseModel):
    sets: list[ProQSet]

    @classmethod
    def load_proqsets_from_file(cls, proq_file: str):
        """Loads the proq sets from a file and returns"""
        md_file = relative_env.get_template(proq_file).render()
        yaml_header, md_string = md_file.split("---", 2)[1:]
        yaml_config = YamlConfig.model_validate(yaml.safe_load(yaml_header))

        return cls(
            sets=[
                {
                    "name": set_name,
                    "proqs": [
                        yaml_config.proq_config
                        | proq
                        | {
                            "title": title,
                            "Solution": (
                                Solution.from_solution_template(
                                    extract_codeblock_content(proq["Solution"])
                                ).model_dump()
                                | yaml_config.solution_config
                            ),
                            "Public Test Cases": extract_testcases(
                                proq["Public Test Cases"]
                            ),
                            "Private Test Cases": extract_testcases(
                                proq["Private Test Cases"]
                            ),
                        }
                        for title, proq in proqs.items()
                    ],
                }
                for set_name, proqs in dictify(md_string).items()
            ]
        )
