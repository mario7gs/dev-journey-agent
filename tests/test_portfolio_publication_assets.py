from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_portfolio_presentation_assets_follow_the_brand_contract() -> None:
    deck = (ROOT / "artifacts/portfolio/DEV_JOURNEY_PORTFOLIO_DECK.html").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "DEV JOURNEY" in deck
    assert "AGENT · FEATURE PLANNING COPILOT" in deck
    assert "A clearer way to start software work." in deck
    assert "Why it can be trusted" in deck
    assert "position:sticky" in deck
    assert "@media print" in deck
    assert 'href="#product"' in deck
    assert 'href="#evidence"' in deck
    assert 'href="../../README.md"' in deck
    assert "PORTFOLIO_PUBLICATION_KIT.md" not in deck
    assert "What this project does" in readme
    assert "Why this project matters" in readme
    assert "Most delivery problems do not start in code." in readme
    assert "When a material gap remains, it stops" in readme
    assert "DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf" in readme
    assert "PORTFOLIO_HANDOFF.md" in readme
    assert not (ROOT / "docs/PORTFOLIO_PUBLICATION_KIT.md").exists()
    assert (ROOT / "artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf").is_file()
    assert (ROOT / "artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pptx").is_file()
    assert (ROOT / "CONTRIBUTING.md").is_file()
    assert (ROOT / "SECURITY.md").is_file()
