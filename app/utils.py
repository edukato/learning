def awesome_date(date):
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
              'декабря']
    return str(date.day) + ' ' + months[date.month - 1] + ' ' + str(date.year)
