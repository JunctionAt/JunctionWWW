__author__ = 'hansihe'

import app


def test_user_player_uuid():
    NAME1 = "testName"
    NAME2 = "anotherName"

    with app.application.app_context():
        import blueprints.auth.user_model as user_model
        player_uuid = user_model.PlayerUUID()
        player_uuid.uuid = "1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"

        # Set initial name
        player_uuid.checkin_mcname(NAME1)
        player_uuid.validate()
        assert player_uuid.mcname == NAME1
        assert len(player_uuid.seen_mcnames) == 1

        # Check in initial name again. Should only update the latest history entry
        player_uuid.checkin_mcname(NAME1)
        player_uuid.validate()
        assert player_uuid.mcname == NAME1
        assert len(player_uuid.seen_mcnames) == 1

        # Check in a new name. Should create a new history entity
        player_uuid.checkin_mcname(NAME2)
        player_uuid.validate()
        assert player_uuid.mcname == NAME2
        assert len(player_uuid.seen_mcnames) == 2

        # Check in the first name again. Should add a new history entry
        player_uuid.checkin_mcname(NAME1)
        player_uuid.validate()
        assert player_uuid.mcname == NAME1
        assert len(player_uuid.seen_mcnames) == 3

        assert len(player_uuid.find_seen_mcname(NAME1)) == 2
        assert len(player_uuid.find_seen_mcname(NAME2)) == 1