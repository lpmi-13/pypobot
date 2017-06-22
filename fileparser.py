import re

HAVE_AUX_FORMS = [
    'have', 'has', 'had', 'having'
]

DO_AUX_FORMS = [
    'do', 'does', 'did', 'doing', 'done'
]

MODAL_AUX_FORMS = [
    'will', 'can', 'shall', 'would', 'could', 'should', 'may', 'might', 'must'
]

def parsefile(original_array, aux_list, form, correction_form):

    correction_array = original_array 


    while len(aux_list) > 0:

        aux_verb = aux_list.pop(0)

        phrase = '{} {}'.format(aux_verb, form)
        suggestion_phrase = '{} {}'.format(aux_verb, correction_form)

        for line in correction_array:
            #iterate through array of lines and do a raw_input prompt
            current_index = correction_array.index(line)

            if (line.find(phrase) > -1):
                found_at = [m.start() for m in re.finditer(phrase, line)]
                suggestion = line.replace(phrase, suggestion_phrase, len(found_at))
                user_input = raw_input('would you like to change: \n\n {} \n\n into \n\n {} ...?\n\n (y/n)'.format(line, suggestion))

                if (user_input is 'y' or 'Y'):
                    correction_array[current_index] = suggestion
                else:
                    correction_array[current_index] = line
            else:
                correction_array[current_index] = line


    return correction_array
