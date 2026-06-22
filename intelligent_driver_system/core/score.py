driver_score = 100

def update_score(state):

    global driver_score

    if state == "Drowsy":
        driver_score -= 1

    elif state == "Very Drowsy":
        driver_score -= 2

    elif state == "Critical":
        driver_score -= 5

    elif state == "Mobile Usage":
        driver_score -= 3

    if driver_score < 0:
        driver_score = 0

    return driver_score