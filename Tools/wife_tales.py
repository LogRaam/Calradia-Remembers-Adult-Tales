# Generates the six other wife tales (Gabriel, 11/10/2026) on the shape of "Beneath the Falls" (Khuzait):
# found [-> watch more ...] -> together -> free states (each to every other and to the invitation) -> invitation
# [-> further moments] [-> afterwards] -> reward. Images are copied from "Image tests 2026-10-10/Wife tale <Nation>".
# Gabriel (11/10/2026): several moments (or several afterwards) are not steps to click through one by one but STATES of
# one moment, like the body states before the invitation: each reached by what the player says or does, each its picture.
# A chain of two or more becomes such a group: the invitation leads to any of them, each to every other, and one way out
# ("You are together"; afterwards, "Back to the camp").
import json, os, shutil

ROOT = r"V:\OneDrive\Programmation\GIT Workspace\Bannerlord LLM project"
SRC = ROOT + r"\Image tests 2026-10-10"
DST = ROOT + r"\Calradia Remembers Adult Tales\ModuleData\cr_quests"

STATE = {
 "shoulder": ("Her shoulder", "the player's attention turns to her shoulder or neck, or her wet dress slips from it"),
 "breast":   ("Her breast", "the player's gaze or touch turns to her breasts"),
 "hips":     ("Her hips", "the player's gaze or touch turns to her hips and backside, or she turns and presses back against the player"),
 "belly":    ("Her belly", "the player's gaze or touch turns to her belly and waist"),
 "legs":     ("Her legs", "the player's gaze or touch turns to her legs, or she lifts the hem of her dress"),
}

def said(meaning): return {"to": "{giver}", "meaning": meaning}

def build(n):
    stages = [{"id": "invite", "journal": n["invite_journal"], "objective": {"type": "talk_to", "hero": "{giver}"}, "on_complete": {"next": n["found"][0]["id"]}}]
    found = n["found"]
    first_after_found = n.get("approach", [{"id": "together"}])[0]["id"]
    for i, f in enumerate(found):
        choices = []
        if len(found) >= 2:
            # Gabriel (11/10/2026): the ways she is found are optional states to explore, not steps: each leads to every other.
            choices += [{"id": o["id"], "label": o["label"], "said": said(o["meaning"]), "next": o["id"]} for o in found if o["id"] != f["id"]]
        choices.append({"id": "joins", "label": "She comes to you", "said": said("she sees the player and wades over to them, or the player goes to her, and they come close together"), "next": first_after_found})
        stages.append({"id": f["id"], "journal": f["journal"], "image": f["image"], "canvas": f["canvas"], "choices": choices})
    for a in n.get("approach", []):
        if a["id"] == "together": continue
        stages.append({"id": a["id"], "journal": a["journal"], "image": a["image"], "canvas": a["canvas"],
                       "choices": [{"id": "together", "label": "She reaches you", "said": said("she reaches the player and takes their hand, or they meet in the water"), "next": "together"}]})

    states = n["states"]  # list of dicts id/image/canvas/journal/label/meaning
    inv = n["invitations"]  # list of {id, label, meaning, image, canvas, journal, then: [moments]}
    def ways(exclude):
        w = [{"id": s["id"], "label": s["label"], "said": said(s["meaning"]), "next": s["id"]} for s in states if s["id"] != exclude]
        w += [{"id": i["id"], "label": i["label"], "said": said(i["meaning"]), "next": i["id"]} for i in inv]
        return w
    t = n["together"]
    stages.append({"id": "together", "journal": t["journal"], "image": t["image"], "canvas": t["canvas"], "choices": ways("together")})
    for s in states:
        stages.append({"id": s["id"], "journal": s["journal"], "image": s["image"], "canvas": s["canvas"], "choices": ways(s["id"])})

    after = n.get("after", [])
    end_target = after[0]["id"] if after else "reward"
    together_way = {"id": "as_one", "label": "You are together", "said": said("they make love, or their lovemaking reaches its end"), "next": end_target}
    for i in inv:
        moments = i.get("then", [])
        if len(moments) >= 2:
            # States of one moment: from the invitation to any of them, from each to every other, one way out.
            def to(m): return {"id": m["id"], "label": m["label"], "said": said(m["meaning"]), "next": m["id"]}
            choices = [to(m) for m in moments]
            for alt in i.get("alt", []):
                choices.append({"id": "turn_" + alt["to"], "label": alt["label"], "said": said(alt["meaning"]), "next": alt["to"]})
            choices.append({"id": "back", "label": "Not yet", "said": said("they linger and return to the water together, not yet ready"), "next": "together"})
            stages.append({"id": i["id"], "journal": i["journal"], "image": i["image"], "canvas": i["canvas"], "choices": choices})
            for m in moments:
                stages.append({"id": m["id"], "journal": m["journal"], "image": m["image"], "canvas": m["canvas"],
                               "choices": [to(o) for o in moments if o["id"] != m["id"]] + [together_way]})
            continue
        chain = [i] + moments
        for k, st in enumerate(chain):
            choices = []
            if k + 1 < len(chain):
                nxt = chain[k + 1]
                choices.append({"id": "closer", "label": nxt.get("label", "Closer"), "said": said(nxt["meaning"]), "next": nxt["id"]})
            else:
                choices.append({"id": "as_one", "label": "You are together", "said": said("they make love, or their lovemaking reaches its end"), "next": end_target})
            for alt in st.get("alt", []):
                choices.append({"id": "turn_" + alt["to"], "label": alt["label"], "said": said(alt["meaning"]), "next": alt["to"]})
            if k == 0:
                choices.append({"id": "back", "label": "Not yet", "said": said("they linger and return to the water together, not yet ready"), "next": "together"})
            stages.append({"id": st["id"], "journal": st["journal"], "image": st["image"], "canvas": st["canvas"], "choices": choices})
    for k, a in enumerate(after):
        choices = []
        if len(after) >= 2:
            # States of the afterwards, each reached by what the player says or does (Gabriel, 11/10/2026).
            choices += [{"id": o["id"], "label": o["label"], "said": said(o["meaning"]), "next": o["id"]} for o in after if o["id"] != a["id"]]
        choices.append({"id": "rest", "label": "Back to the camp", "said": said("they rest, dress, or speak of going back to the camp"), "next": "reward"})
        stages.append({"id": a["id"], "journal": a["journal"], "image": a["image"], "canvas": a["canvas"], "choices": choices})

    return {
        "id": n["id"], "title": n["title"], "author": "Gabriel Mailhot",
        "requires": {"giver": {"role": "spouse", "gender": "female", "culture": n["culture"], "with_player": True, "not_pregnant": True,
                               "min_regard": 10, "not_at_war_with_player": False}, "content": "explicit"},
        "on_map": {"still_hours": 3, "by_day": True, "in_givers_lands": True, "chance_per_day": 0.15,
                   "invitation": n["popup"], "accept": "Follow her", "decline": "Let her have her solitude"},
        "binds": {"giver": "the player's " + n["people"] + " wife, travelling with them"},
        "stages": stages,
        "reward": {"regard": 8, "memory": n["memory"], "journal": n["reward_journal"],
                   "consequences": [{"type": "conception", "who": "{giver}"}]},
        "failure": {"days": 2}
    }

def st(id, image, canvas, journal, label=None, meaning=None):
    d = {"id": id, "image": image, "canvas": canvas, "journal": journal}
    if id in STATE and label is None: label, meaning = STATE[id]
    if label: d["label"] = label
    if meaning: d["meaning"] = meaning
    return d

NATIONS = []

# ── Aserai: an oasis pool in the desert ──
NATIONS.append({"folder": "Aserai", "id": "crit_wife_aserai_oasis", "title": "The Hidden Oasis", "culture": "aserai", "people": "Aserai",
 "popup": "In the heat of the afternoon, while your company rests in the shade of the dunes, {giver} takes a water skin and walks toward the palms of a hidden oasis. She looks back at you over her shoulder, a slow smile, and goes on alone.",
 "invite_journal": "{giver} walked off toward the palms of a hidden oasis.",
 "found": [st("found", "1_found_bathing.jpg", "You walked to the hidden oasis to bathe in its cool green water, in your thin embroidered robe and your beads, while the camp rests through the heat. You know the player followed you; you let them find you, and you are glad of it.", "You found {giver} bathing in the oasis.")],
 "together": st("together", "3_she_joins_him.jpg", "You have walked out of the water to the player, the wet robe clinging to you, smiling. An hour alone with your spouse, far from the camp, in the land of your people.", "{giver} has come to you."),
 "states": [st("shoulder", "2_shoulder.jpg", "The wet robe clings to your shoulder and your beads lie warm on your skin; you let the player look, wholly at ease.", "{giver}'s shoulder."),
            st("breast", "4a_breast.jpg", "The player admires your breasts through the soaked robe, and you welcome it.", "You admire {giver}."),
            st("breast_shy", "4b_breast.jpg", "You fold your arms over your breasts, teasing the player, letting them wait.", "{giver} teases you.", "She teases you", "she folds her arms over her breasts, playful, making the player wait"),
            st("hips", "5a_hips.jpg", "You have turned your back to the player in the shallows, your hands on your hips, the wet robe clinging to you.", "{giver} turns her back to you."),
            st("hips_close", "5b_hips.jpg", "The player is close behind you, and you lean back against them.", "{giver} leans back against you.", "Closer behind her", "the player comes close behind her, or she leans back against the player"),
            st("belly", "6a_belly.jpg", "You lift the wet robe from your belly, slowly, watching the player watch you.", "{giver} lifts her robe."),
            st("belly_close", "6b_belly_closeup.jpg", "The player's touch is on your belly and waist, and you shiver in the heat.", "You touch {giver}.", "Your touch", "the player's hand or lips are on her belly and waist"),
            st("legs", "7_legs.jpg", "You gather your robe above your knees and step through the shallows toward the player.", "{giver} lifts the hem of her robe.")],
 "invitations": [{"id": "invitation", "label": "She draws you down onto the sand", "meaning": "she draws the player down onto the warm sand and comes over them, inviting them",
                  "image": "8a_invitation.jpg", "canvas": "You have drawn the player down onto the warm sand and you lean over them, your braids falling around you, inviting them.", "journal": "{giver} draws you down onto the sand.",
                  "then": [st("above_you", "8b_invitation.jpg", "You are with the player on the warm sand under the evening sky, above them.", "With {giver} under the evening sky.", "She is above you", "she is above the player on the warm sand, under the evening sky"),
                           st("nothing_held_back", "8c_invitation.jpg", "You and the player are lovers under the burning sky; you hold nothing back.", "With {giver}.", "Nothing held back", "they give themselves to each other wholly, holding nothing back"),
                           st("her_hands", "8d_invitation.jpg", "You guide the player's hands to you as the sun goes down.", "With {giver}.", "She guides your hands", "she takes the player's hands and guides them to her"),
                           st("her_glow", "8e_invitation.jpg", "You smile down at the player, glowing in the last light.", "With {giver}.", "She smiles down at you", "she smiles down at the player, glowing in the last light"),
                           st("laughing", "8f_invitation.jpg", "You lie with the player in the warm sand, laughing softly.", "With {giver}.", "Laughing in the sand", "they lie together in the warm sand and laugh softly"),
                           st("burning_sky", "8g_invitation.jpg", "The sky burns above you both; you are wholly the player's and they are yours.", "With {giver}.", "Under the burning sky", "the sky burns above them and they are wholly each other's")]}],
 "after": [st("after", "9a_pretty_smile.jpg", "It is over, and you lie in the warm sand with the player, smiling, in no hurry to go back.", "Afterwards, {giver} smiles at you.", "Resting together", "they rest together afterwards in the warm sand"),
           st("her_smile", "9b_pretty_smile.jpg", "You smile at the player, sand on your skin, happy.", "{giver} smiles.", "Her happy smile", "she smiles at the player, happy, sand on her skin"),
           st("at_sunset", "9c_pretty_face.jpg", "The sun is setting; you look at the player a long while, content.", "{giver} looks at you.", "As the sun sets", "the sun sets and she looks at the player a long while, content")],
 "memory": "An afternoon at a hidden oasis in the land of my people, when my spouse followed me and we were alone together until sunset.",
 "reward_journal": "An afternoon at the hidden oasis that neither of you will forget."})

# ── Battania: a forest waterfall ──
NATIONS.append({"folder": "Battania", "id": "crit_wife_battania_glen", "title": "The Glen of the Falls", "culture": "battania", "people": "Battanian",
 "popup": "While your company makes camp under the oaks, {giver} slips away down a path toward the sound of a waterfall in the glen, her plaid over her arm. She glances back at you once, and the green swallows her.",
 "invite_journal": "{giver} slipped away toward a waterfall in the glen.",
 "found": [st("found", "1a_found_bathing.jpg", "You went down to bathe beneath the falls in the glen, as the women of your people do, bare to the waist, your plaid knotted at your hips. You know the player followed; you let them watch, and you take your time.", "You found {giver} bathing in the glen.", "Bathing in the glen", "she bathes beneath the falls, bare to the waist, and the player watches her"),
           st("crouching", "1b_observe_more_bathing.jpg", "You crouch in the pool to wash, knowing the player is watching, and you do not hurry.", "{giver} bathes, unhurried.", "She crouches to wash", "she crouches in the pool to wash, unhurried, knowing the player watches"),
           st("under_the_falls", "1c_observe_even_more_bathing.jpg", "You kneel in the water beneath the falls and let it run over you, aware of the player's eyes.", "{giver} kneels beneath the falls.", "She kneels under the falls", "she kneels in the water beneath the falls and lets it run over her")],
 "together": st("together", "3_she_joins_him.jpg", "You have come up out of the pool to the player, wet and smiling, your braid over your shoulder. An hour alone with your spouse, in the land of your people.", "{giver} has come to you."),
 "states": [st("shoulder", "2_shoulder.jpg", "Water runs over your freckled shoulder; you let the player look.", "{giver}'s shoulder."),
            st("breast", "4_breast.jpg", "The player admires your breasts, and you welcome it.", "You admire {giver}."),
            st("hips", "5_hips.jpg", "You have turned your back to the player, your plaid low on your hips.", "{giver} turns her back to you."),
            st("belly", "6_belly.jpg", "The player's gaze is on your belly above the knot of your plaid.", "You admire {giver}."),
            st("legs", "7_legs.jpg", "You draw your wet plaid up over your thigh, watching the player.", "{giver} draws up her plaid.")],
 "invitations": [{"id": "invitation", "label": "She lies down and invites you", "meaning": "she lies back on the moss by the pool and invites the player to her",
                  "image": "8_invitation.jpg", "canvas": "You have lain back on the moss among the ferns and you look up at the player, inviting them to you.", "journal": "{giver} lies back on the moss and reaches for you."}],
 "memory": "A day in the glen of my people, when my spouse followed me to the falls and we were alone together.",
 "reward_journal": "A day in the glen that neither of you will forget."})

# ── Empire: a forest stream ──
NATIONS.append({"folder": "Empire", "id": "crit_wife_empire_stream", "title": "The Stream in the Wood", "culture": "empire", "people": "imperial",
 "popup": "While your company rests in the shade of the wood, {giver} unpins her hair and walks down toward a clear stream, her gold armband glinting. At the trees she turns, smiles at you, and goes on.",
 "invite_journal": "{giver} walked down toward a stream in the wood.",
 "found": [st("found", "1_found_bathing.jpg", "You went down to bathe in the clear stream in your thin draped dress, as the ladies of the Empire do in summer. You know the player followed you; you let them find you.", "You found {giver} bathing in the stream.")],
 "approach": [st("approach", "3a_before_she_joins_him.jpg", "You have seen the player and you wade toward them through the stream, the wet drapery slipping, smiling.", "{giver} wades toward you.")],
 "together": st("together", "3b_she_joins_him.jpg", "You have reached the player and taken their hand, laughing, drawing them into the water. An hour alone with your spouse, in the land of your people.", "{giver} takes your hand."),
 "states": [st("shoulder", "2_shoulder.jpg", "Your drapery has slipped to your arm, baring your shoulder; you let the player look.", "{giver}'s shoulder."),
            st("breast", "4a_breast.jpg", "The player admires your breasts beneath the wet drapery, and you welcome it.", "You admire {giver}."),
            st("breast_bare", "4b_breast_nude.jpg", "You let the wet drapery fall from your breasts for the player.", "{giver} lets her drapery fall.", "Her drapery falls", "she lets the drapery fall from her breasts, or the player draws it down"),
            st("hips", "5_hips.jpg", "You have turned your back to the player, lifting the wet drapery from your hips.", "{giver} turns her back to you."),
            st("belly", "6_belly.jpg", "The player's gaze is on your belly where the drapery hangs low.", "You admire {giver}."),
            st("legs", "7_legs.jpg", "You gather the wet drapery above your knees in the stream.", "{giver} lifts her drapery.")],
 "invitations": [{"id": "invitation", "label": "She draws you into the meadow", "meaning": "she leads the player out of the water into the flowering meadow and sits among the flowers, inviting them",
                  "image": "8a_meadow.jpg", "canvas": "You have led the player out of the stream into a meadow of wild flowers, and you sit among them, inviting them to you.", "journal": "{giver} sits among the flowers and calls you.",
                  "then": [st("meadow", "8b_meadow.jpg", "You lie back among the flowers, smiling up at the player, your drapery fallen open.", "{giver} lies back among the flowers.", "She lies back among the flowers", "she lies back among the flowers and draws the player down to her")]}],
 "memory": "A summer day in the land of my people, when my spouse followed me to a stream in the wood and we lay together in a meadow of flowers.",
 "reward_journal": "A day by the stream that neither of you will forget."})

# ── Vlandia: a lily pond ──
NATIONS.append({"folder": "Vlandia", "id": "crit_wife_vlandia_pond", "title": "The Lily Pond", "culture": "vlandia", "people": "Vlandian",
 "popup": "While your company makes camp by the meadows, {giver} takes off her shoes and walks toward a still pond among the willows, in only her linen shift. She looks back at you once from the bank, and steps out of sight.",
 "invite_journal": "{giver} walked toward a lily pond among the willows.",
 "found": [st("found", "1_found_bathing.jpg", "You went to bathe in the lily pond in your thin lace shift. You know the player followed you; you let them watch, and you take your time.", "You found {giver} bathing in the lily pond.", "Bathing among the lilies", "she bathes in the lily pond in her lace shift and the player watches her"),
           st("among_the_lilies", "1b_observe_her_more.jpg", "You kneel in the shallow water among the lilies, knowing the player watches.", "{giver} kneels among the lilies.", "She kneels among the lilies", "she kneels in the shallow water among the lilies, knowing the player watches"),
           st("looking_back", "2c_observe_evenm_more.jpg", "You lift the hem of your wet shift and look back over your shoulder at the player.", "{giver} looks back at you.", "She looks back at you", "she lifts the hem of her wet shift and looks back over her shoulder at the player")],
 "together": st("together", "3_she_joins_him.jpg", "You have walked out of the pond to the player in your soaked shift, smiling. An hour alone with your spouse, in the land of your people.", "{giver} has come to you."),
 "states": [st("shoulder", "2_shoulder.jpg", "Your wet shift clings to your shoulder; you let the player look.", "{giver}'s shoulder."),
            st("breast", "4_breast.jpg", "The player admires your breasts through the soaked lace, and you welcome it.", "You admire {giver}."),
            st("hips", "5_hips.jpg", "You have turned your back to the player at the water's edge, lifting your shift.", "{giver} turns her back to you."),
            st("belly", "6_belly.jpg", "You draw the wet shift up from your belly, watching the player.", "{giver} draws up her shift."),
            st("legs", "7_legs.jpg", "You kneel on the bank, your wet legs bare beneath the lace.", "{giver} kneels on the bank.")],
 "invitations": [
   {"id": "invitation", "label": "She lies down on the grass", "meaning": "she lies down on her front in the grass by the pond and looks back at the player, inviting them",
    "image": "8a_invitation.jpg", "canvas": "You have lain down on your front in the grass by the pond and you look back at the player, inviting them.", "journal": "{giver} lies down in the grass.",
    "alt": [{"to": "invitation_up", "label": "She rises on her elbows", "meaning": "she rises on her elbows and looks back at the player"}],
    "then": [st("invitation_next", "8b_invitation_next_step.jpg", "The player has drawn your shift up, and you welcome them.", "With {giver} in the grass.", "Closer", "the player draws her shift up, or their lovemaking begins")]},
   {"id": "invitation_up", "label": "She rises on her elbows", "meaning": "she lies on her front in the grass, propped on her elbows, looking back at the player",
    "image": "8a_invitation_alternative.jpg", "canvas": "You lie on your front in the grass, propped on your elbows, looking back at the player.", "journal": "{giver} looks back at you from the grass.",
    "then": [st("invitation_up_next", "8b_invitation_alternative_next_step.jpg", "Your shift has slipped down your back, and you welcome the player.", "With {giver} in the grass.", "Closer", "her shift slips down, or their lovemaking begins")]},
   {"id": "invitation_back", "label": "She lies on her back", "meaning": "she lies down on her back among the leaves and invites the player to her",
    "image": "8a_other_invitation.jpg", "canvas": "You have lain down on your back among the leaves and ferns and you reach for the player.", "journal": "{giver} lies back among the leaves.",
    "then": [st("invitation_back_next", "8b_other_invitation_next_step.jpg", "You draw your shift up for the player, inviting them closer.", "With {giver} among the leaves.", "Closer", "she draws her shift up, or their lovemaking begins")]}],
 "memory": "A summer day in the land of my people, when my spouse followed me to the lily pond and we were alone together.",
 "reward_journal": "A day by the lily pond that neither of you will forget."})

# ── Sturgia: a waterfall in the birch forest ──
NATIONS.append({"folder": "Sturgia", "id": "crit_wife_sturgia_falls", "title": "The Birch Falls", "culture": "sturgia", "people": "Sturgian",
 "popup": "While your company makes camp among the birches, {giver} braids her hair and walks toward the roar of a waterfall, a linen cloth over her arm. She glances back at you from the trees, once, and is gone.",
 "invite_journal": "{giver} walked toward a waterfall among the birches.",
 "found": [st("found", "1_found_bathing.jpg", "You went to bathe beneath the falls in your long embroidered linen dress, in the short northern summer. You know the player followed you; you let them find you.", "You found {giver} bathing beneath the falls.")],
 "together": st("together", "3_she_joins_him.jpg", "You have waded to the player in your soaked dress, smiling, your braid over your shoulder. An hour alone with your spouse, in the land of your people.", "{giver} has come to you."),
 "states": [st("shoulder", "2_shoulder.jpg", "The wet linen clings to your shoulder; you let the player look.", "{giver}'s shoulder."),
            st("breast", "4_breast.jpg", "The player admires your breasts through the soaked linen, and you welcome it.", "You admire {giver}."),
            st("hips", "5_hips.jpg", "You have turned your back to the player and lifted your wet dress from your hips.", "{giver} turns her back to you."),
            st("belly", "6_belly.jpg", "The wet dress hangs open over your belly; you watch the player look.", "You admire {giver}."),
            st("legs", "7_legs.jpg", "You lift the wet hem of your dress above your thighs for the player.", "{giver} lifts the hem of her dress.")],
 "invitations": [{"id": "invitation", "label": "She sits on the bank and invites you", "meaning": "she sits down on the mossy bank by the falls and invites the player to her",
                  "image": "8_invitation.jpg", "canvas": "You have sat down on the mossy bank, your wet dress fallen from your shoulders, and you look at the player, inviting them.", "journal": "{giver} sits on the bank and calls you.",
                  "then": [st("lies_down", "9_she_lay_down.jpg", "You lie back on the moss, your hair spread around you, and draw the player down to you.", "{giver} lies back on the moss.", "She lies back", "she lies back on the moss and draws the player down to her")]}],
 "memory": "A summer day in the land of my people, when my spouse followed me to the falls among the birches and we were alone together.",
 "reward_journal": "A day by the birch falls that neither of you will forget."})

# ── Nords: a cold plunge in the fjord ──
NATIONS.append({"folder": "Nords", "id": "crit_wife_nord_fjord", "title": "The Cold Water", "culture": "nord", "people": "Nord",
 "popup": "While your company makes camp above the fjord, {giver} walks down to the icy shore in only her wool shift, as the women of her people do to harden themselves against the winter. She looks back up at you, laughing, and wades in.",
 "invite_journal": "{giver} went down to the fjord for the cold plunge of her people.",
 "found": [st("found", "1_found_bathing.jpg", "You went down to plunge into the icy fjord in your thin wool shift, as the women of your people do. You know the player followed you; let them see that the cold does not frighten you.", "You found {giver} in the icy fjord.")],
 "together": st("together", "3_she_joins_him.jpg", "You have waded out of the icy water to the player, laughing, red with the cold, your shift clinging to you. Their warmth is what you want now.", "{giver} comes out of the icy water to you."),
 "states": [st("shoulder", "2_shoulder.jpg", "Your shoulder is red with the cold and wet with the fjord; you let the player look.", "{giver}'s shoulder."),
            st("breast", "4_breast.jpg", "You fold your arms over your breasts against the cold, and look at the player boldly.", "You admire {giver}."),
            st("hips", "5_hips.jpg", "You have turned your back to the player in the icy shallows, your wet shift clinging to you.", "{giver} turns her back to you."),
            st("belly", "6_belly.jpg", "The player's warm hand is on your cold belly, and you laugh at the shock of it.", "You warm {giver}."),
            st("legs", "7_legs.jpg", "You lift your wet shift above your reddened knees in the icy water.", "{giver} lifts her shift.")],
 "invitations": [{"id": "invitation", "label": "She lies down on the shore", "meaning": "she lies back on the stony shore and draws the player to her to be warmed",
                  "image": "8_invitation.jpg", "canvas": "You have lain back on the cold stones of the shore and you draw the player to you; you want their warmth.", "journal": "{giver} lies back on the shore and draws you to her."}],
 "memory": "A cold day by the fjord of my people, when my spouse followed me into the icy water and warmed me after.",
 "reward_journal": "A day by the icy fjord that neither of you will forget."})

SOURCE_NAME = {"9b_pretty_smile.jpg": "9b_pretty smile.jpg", "8a_meadow.jpg": "grok-image-7a4324d6-9192-41e4-8813-193b1cf303a0.jpg", "8b_meadow.jpg": "grok-image-365d843a-eeb9-4645-ab43-7ad632d666dd.jpg"}
made = []
for n in NATIONS:
    q = build(n)
    folder = os.path.join(DST, q["id"].replace("crit_", ""))
    os.makedirs(folder, exist_ok=True)
    used = sorted({s["image"] for s in q["stages"] if s.get("image")})
    src = os.path.join(SRC, "Wife tale " + n["folder"])
    for img in used:
        shutil.copyfile(os.path.join(src, SOURCE_NAME.get(img, img) if os.path.exists(os.path.join(src, SOURCE_NAME.get(img, img))) else img), os.path.join(folder, img))
    with open(os.path.join(folder, q["id"].replace("crit_", "") + ".json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(q, indent=2, ensure_ascii=False) + "\n")
    unused = sorted(set(x for x in os.listdir(src) if x.lower().endswith(".jpg")) - {SOURCE_NAME.get(u, u) for u in used})
    made.append((q["id"], len(q["stages"]), len(used), unused))
for m in made: print(m)
