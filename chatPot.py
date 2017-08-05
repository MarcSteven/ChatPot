GREETING_KEYWORDS = ("hello","hi","greeeings","sup","what's up",)
GREETING_RESPONSES = ["'sup bro","hey","*nods*","hey you get my snap?"']

def check_for_gretting(sentence):
	""" if any of the words in the user' input was a greeting,return a greeeting response"""
	for word in sentence.word:
		if word.lower() in GREETING_KEYWORDS:
			return random.choice(GREETING_RESPONSES)

def respond(sentence):
	"""Parse the user's inbound sentence and find candidate terms taht make up a best-fit response"""
	cleaned = preprocess_text(sentence)
	parsed = TextBlob(cleaned)
	pronoun ,noun,adjective,verb = find_candidate_parts_of_speech(parsed)
	resp = check_for_comment_about_bot(pronoun,noun,adjective)
	if not resp:
		resp = check_for_gretting(parsed)
	if not resp:
		if not pronoun:
			resp = random.choice(NONE_RESPONSE)
		elif pronoun == 'I' and not verb:
			resp = random.choice(COMMENTS_ABOUT_SELF)
		else :
			resp = construct_response(pronoun,noun,verb)
	if not resp:
		resp = random.choice(NONE_RESPONSE)
		logger.info("Return phase %s",resp)
		filter.response(resp)
		return resp
def find_candidate_parts_of_speech(parsed):
	""“given a parsed input,find the bset pronoun,direct noun,adjective,and verb to match their input.
	Returns a tuple pf pronoun,noun,adjective,verb any of which may be None if there was no goood match""
	pronoun = None
	noun = None
	adjective = None
	verb = None
	for sent in parsed.sentence :
		pronoun = find_pronoun(sent)
		noun = find_noun(sent)
		adjective = find_adjective(sent)
		verb = find_verb(sent)
		logger.info("pronoun = %s,noun = %s,adjective = %s,verb = %s",pronoun,noun,adjective,verb)
		return pronoun,noun,adjective,verb
	def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
    pronoun is found in the input"""
    pronoun = None

    for word, part_of_speech in sent.pos_tags:
        # Disambiguate pronouns
        if part_of_speech == 'PRP' and word.lower() == 'you':
            pronoun = 'I'
        elif part_of_speech == 'PRP' and word == 'I':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'You'
    return pronoun

    def check_for_comment_about_bot(pronoun, noun, adjective):
    """Check if the user's input was about the bot itself, in which case try to fashion a response
    that feels right based on their input. Returns the new best sentence, or None."""
    resp = None
    if pronoun == 'I' and (noun or adjective):
        if noun:
            if random.choice((True, False)):
                resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': noun.pluralize().capitalize()})
            else:
                resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        else:
            resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp

# Template for responses that include a direct noun which is indefinite/uncountable
SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "My last startup totally crushed the {noun} vertical",
    "Were you aware I was a serial entrepreneur in the {noun} sector?",
    "My startup is Uber for {noun}",
    "I really consider myself an expert on {noun}",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah but I know a lot about {noun}",
    "My bros always ask me about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "I'm personally building the {adjective} Economy",
    "I consider myself to be a {adjective}preneur",
]

def construct_response(pronoun, noun, verb):
    """No special cases matched, so we're going to try to construct a full sentence that uses as much
    of the user's input as possible"""
    resp = []

    if pronoun:
        resp.append(pronoun)

    # We always respond in the present tense, and the pronoun will always either be a passthrough
    # from the user, or 'you' or 'I', in which case we might need to change the tense for some
    # irregular verbs.
    if verb:
        verb_word = verb[0]
        if verb_word in ('be', 'am', 'is', "'m"):  # This would be an excellent place to use lemmas!
            if pronoun.lower() == 'you':
                # The bot will always tell the person they aren't whatever they said they were
                resp.append("aren't really")
            else:
                resp.append(verb_word)
    if noun:
        pronoun = "an" if starts_with_vowel(noun) else "a"
        resp.append(pronoun + " " + noun)

    resp.append(random.choice(("tho", "bro", "lol", "bruh", "smh", "")))

    return " ".join(resp)

def filter_response(resp):
    """Don't allow any words to match our filter list"""
    tokenized = resp.split(' ')
    for word in tokenized:
        if '@' in word or '#' in word or '!' in word:
            raise UnacceptableUtteranceException()
        for s in FILTER_WORDS:
            if word.lower().startswith(s):
                raise UnacceptableUtteranceException()

