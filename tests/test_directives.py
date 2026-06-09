import unittest

from ming_sim.content import GameContent
from ming_sim.db import GameDB
from ming_sim.models import GameState


class DirectivePersistenceTests(unittest.TestCase):
    def test_directive_without_event_or_actor_uses_null_foreign_keys(self):
        db = GameDB(":memory:", GameContent.load())
        try:
            db.conn.execute("PRAGMA foreign_keys=ON")
            directive_id = db.add_directive(
                GameState(),
                None,
                "敕谕户部赈济陕西",
                "手动新增",
            )

            row = db.conn.execute(
                "SELECT event_id, actor, text, source FROM turn_directives WHERE id=?",
                (directive_id,),
            ).fetchone()
            self.assertIsNone(row["event_id"])
            self.assertIsNone(row["actor"])
            self.assertEqual(row["text"], "敕谕户部赈济陕西")
            self.assertEqual(row["source"], "手动新增")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
