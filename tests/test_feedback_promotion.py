from dataclasses import replace

from gnosis.self_learning.feedback_promotion import (
    create_promotion_record,
    promotion_record_valid,
)


def make(decision="PROMOTED"):
    return create_promotion_record(
        validation_id="sha256:validation",
        proposal_id="sha256:proposal",
        source_delivery_receipt_id="sha256:delivery",
        target_knowledge_revision="knowledge:r2",
        promoted_finding_refs=("finding:1",),
        excluded_refs=("private:1",),
        decision=decision,
        record_revision="r1",
    )


def test_promotion_record_requires_promote_validation():
    assert promotion_record_valid(validation_decision="PROMOTE", record=make())


def test_validation_hold_blocks_record_validity():
    assert not promotion_record_valid(validation_decision="HOLD", record=make())


def test_rejected_record_is_invalid():
    assert not promotion_record_valid(validation_decision="PROMOTE", record=make("REJECTED"))


def test_identity_is_deterministic():
    assert make() == make()


def test_semantic_tampering_breaks_record_identity():
    tampered = replace(make(), promoted_finding_refs=("finding:attacker",))
    assert not promotion_record_valid(validation_decision="PROMOTE", record=tampered)


def test_foreign_provenance_is_rejected():
    record = make()
    assert not promotion_record_valid(
        validation_decision="PROMOTE",
        record=record,
        proposal_id="sha256:foreign-proposal",
    )
    assert not promotion_record_valid(
        validation_decision="PROMOTE",
        record=record,
        source_delivery_receipt_id="sha256:foreign-delivery",
    )
    assert not promotion_record_valid(
        validation_decision="PROMOTE",
        record=record,
        target_knowledge_revision="knowledge:foreign",
    )


def test_foreign_validation_and_findings_are_rejected():
    record = make()
    assert not promotion_record_valid(
        validation_decision="PROMOTE",
        record=record,
        validation_id="sha256:foreign-validation",
    )
    assert not promotion_record_valid(
        validation_decision="PROMOTE",
        record=record,
        promoted_finding_refs=("finding:foreign",),
    )
    assert not promotion_record_valid(
        validation_decision="PROMOTE",
        record=record,
        excluded_refs=("private:foreign",),
    )


def test_record_is_frozen():
    record = make()
    try:
        record.proposal_id = "sha256:foreign-proposal"
    except Exception:
        pass
    else:
        raise AssertionError("promotion record must be immutable")
