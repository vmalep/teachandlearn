from django import forms
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _


class AvailabilityWidget(forms.Widget):
    DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    DAY_LABELS = {
        'mon': _('Mon'), 'tue': _('Tue'), 'wed': _('Wed'),
        'thu': _('Thu'), 'fri': _('Fri'), 'sat': _('Sat'), 'sun': _('Sun'),
    }
    PERIODS = ['morning', 'afternoon', 'evening']
    PERIOD_LABELS = {
        'morning': _('Morning'), 'afternoon': _('Afternoon'), 'evening': _('Evening'),
    }

    def value_from_datadict(self, data, files, name):
        result = {}
        for day in self.DAYS:
            result[day] = {}
            for period in self.PERIODS:
                result[day][period] = f"{name}_{day}_{period}" in data
        return result

    def render(self, name, value, attrs=None, renderer=None):
        if not value or not isinstance(value, dict):
            value = {day: {p: False for p in self.PERIODS} for day in self.DAYS}

        header_cells = ['<th class="w-24"></th>']
        for day in self.DAYS:
            header_cells.append(
                f'<th class="text-center text-xs font-medium text-slate-700 py-2 px-2 w-10">'
                f'{self.DAY_LABELS[day]}</th>'
            )

        rows = []
        for period in self.PERIODS:
            cells = [
                f'<td class="pr-4 py-2 text-xs text-slate-500 whitespace-nowrap">'
                f'{self.PERIOD_LABELS[period]}</td>'
            ]
            for day in self.DAYS:
                checked = 'checked' if (value.get(day) or {}).get(period) else ''
                input_name = f"{name}_{day}_{period}"
                cells.append(
                    f'<td class="text-center py-2 px-2">'
                    f'<input type="checkbox" name="{input_name}" {checked} '
                    f'class="w-4 h-4 rounded accent-violet-600 cursor-pointer">'
                    f'</td>'
                )
            rows.append('<tr>' + ''.join(cells) + '</tr>')

        html = (
            '<div class="overflow-x-auto">'
            '<table class="border-collapse">'
            '<thead><tr>' + ''.join(header_cells) + '</tr></thead>'
            '<tbody>' + ''.join(rows) + '</tbody>'
            '</table>'
            '</div>'
        )
        return mark_safe(html)
