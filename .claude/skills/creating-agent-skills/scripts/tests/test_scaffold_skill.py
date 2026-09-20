import pytest

from scripts.scaffold_skill import scaffold_skill, slug_to_title, validate_name


def test_slug_to_title_converts_kebab_case():
    assert slug_to_title("creating-agent-skills") == "Creating Agent Skills"


def test_slug_to_title_single_word():
    assert slug_to_title("grilling") == "Grilling"


@pytest.mark.parametrize(
    "name",
    ["grilling", "grill-with-docs", "a", "a1-b2"],
)
def test_validate_name_accepts_kebab_case(name):
    validate_name(name)  # should not raise


@pytest.mark.parametrize(
    "name",
    ["Grilling", "grill_with_docs", "grill with docs", "-leading-hyphen", "trailing-", ""],
)
def test_validate_name_rejects_invalid_names(name):
    with pytest.raises(ValueError):
        validate_name(name)


def test_scaffold_skill_creates_skill_md(tmp_path):
    skill_dir = scaffold_skill(tmp_path, "my-skill")

    assert skill_dir == tmp_path / "my-skill"
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "name: my-skill" in content
    assert "# My Skill" in content


def test_scaffold_skill_uses_custom_description(tmp_path):
    skill_dir = scaffold_skill(tmp_path, "my-skill", description="カスタム説明")
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "カスタム説明" in content


def test_scaffold_skill_rejects_invalid_name(tmp_path):
    with pytest.raises(ValueError):
        scaffold_skill(tmp_path, "Invalid_Name")


def test_scaffold_skill_raises_if_directory_exists(tmp_path):
    scaffold_skill(tmp_path, "my-skill")
    with pytest.raises(FileExistsError):
        scaffold_skill(tmp_path, "my-skill")


def test_scaffold_skill_default_has_no_optional_dirs(tmp_path):
    skill_dir = scaffold_skill(tmp_path, "my-skill")
    assert not (skill_dir / "scripts").exists()
    assert not (skill_dir / "agents").exists()
    assert not (skill_dir / "references").exists()


def test_scaffold_skill_with_scripts_creates_test_stub(tmp_path):
    skill_dir = scaffold_skill(tmp_path, "my-skill", with_scripts=True)
    assert (skill_dir / "scripts" / "__init__.py").exists()
    assert (skill_dir / "scripts" / "tests" / "__init__.py").exists()
    assert (skill_dir / "scripts" / "tests" / "test_my_skill.py").exists()


def test_scaffold_skill_with_agents_creates_example(tmp_path):
    skill_dir = scaffold_skill(tmp_path, "my-skill", with_agents=True)
    assert (skill_dir / "agents" / "example.md").exists()


def test_scaffold_skill_with_references_creates_example(tmp_path):
    skill_dir = scaffold_skill(tmp_path, "my-skill", with_references=True)
    assert (skill_dir / "references" / "example.md").exists()
