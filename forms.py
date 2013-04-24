from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(label='Upload file')

class ApiForm(forms.Form):
    MONTH_CHOICES = (
        (1, 'Jan'),
        (2, 'Feb'),
        (3, 'Mar'),
        (4, 'Apr'),
        (5, 'May'),
        (6, 'Jun'),
        (7, 'Jul'),
        (8, 'Aug'),
        (9, 'Sep'),
        (10, 'Oct'),
        (11, 'Nov'),
        (12, 'Dec')
    )

    days = []
    for d in range(31):
        d = d+1
        tup = (d, str(d))
        days.append(tup)

    DAY_CHOICES = tuple(days)

    username = forms.CharField(label='Enter your Delicious username')
    password = forms.CharField(widget=forms.PasswordInput, label='Enter your Delicious password')

    from_month = forms.ChoiceField(widget=forms.Select(attrs={'class':'span1'}), label='Month', choices=MONTH_CHOICES)
    from_day = forms.ChoiceField(widget=forms.Select(attrs={'class':'span1'}), label='Day', choices=DAY_CHOICES)
    from_year = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'span2'}), label='Year', help_text='Enter 4 digit year')

    to_month = forms.ChoiceField(widget=forms.Select(attrs={'class':'span1'}), label='Month', choices=MONTH_CHOICES)
    to_day = forms.ChoiceField(widget=forms.Select(attrs={'class':'span1'}), label='Day', choices=DAY_CHOICES)
    to_year = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'span2'}), label='Year', help_text='Enter 4 digit year')

    tags = forms.CharField(label='Enter tags', help_text='Separate tags with a comma.')
    
