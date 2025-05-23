# Allowance Calculator for Home Assistant

A Home Assistant component that calculates and tracks allowances for children based on their age. Perfect for parents who want to automate allowance management and get notifications when a child's allowance should increase.

## Features

- **Age-Based Calculation**: Automatically calculates allowances based on the child's age
- **Birthday Notifications**: Sends a notification when it's a child's birthday and their allowance increases
- **Multiple Children**: Support for multiple children with different configurations
- **Currency Support**: Configure your preferred currency (EUR by default)
- **Custom Percentages**: Set different percentage rates for each child
- **UI Configuration**: Full configuration via the Home Assistant UI
- **YAML Configuration**: Alternative YAML-based configuration

## Installation

1. Download the latest release from [GitHub](https://github.com/xblackbytesx/ha-allowance-calculator/releases)
2. Extract the contents
3. Copy the `allowance_calculator` folder to your Home Assistant `custom_components` directory:
   ```
   custom_components/allowance_calculator/
   ```
4. Restart Home Assistant

## Configuration

### Option 1: Using the UI

1. Go to **Settings** → **Devices & Services**
2. Click the **+ ADD INTEGRATION** button in the bottom right
3. Search for "Allowance Calculator" and select it
4. Follow the setup wizard:
   - Select your preferred currency
   - Add each child with their name, birthday, and percentage rate
   - Choose whether to add additional children

### Option 2: Using configuration.yaml

Add the following to your `configuration.yaml` file:

```yaml
allowance_calculator:
  currency: EUR  # Optional, defaults to EUR
  children:
    - name: Alice
      birthday: "2015-06-15"  # Format: YYYY-MM-DD
      percentage: 30  # Optional, defaults to 30
    - name: Bob
      birthday: "2013-03-10"
      percentage: 35
    - name: Charlie
      birthday: "2010-12-25"
```

## How It Works

The component creates a sensor entity for each child with the format `sensor.[child_name]_allowance`.

### Calculation Method

The allowance is calculated using the formula:

```
allowance = age × percentage ÷ 100
```

Where:
- `age` is the child's current age in years
- `percentage` is the configured percentage (default: 30)

For example, a 10-year-old child with the default 30% rate would get an allowance of 3.00 (10 × 30 ÷ 100).

### Sensor Attributes

Each sensor includes these attributes:
- `age`: Current age in years
- `birthday`: The child's birth date
- `percentage`: The percentage rate used for calculation
- `formatted_value`: The allowance formatted with the currency symbol
- `days_until_birthday`: Number of days until the next birthday
- `next_allowance`: The allowance amount after the next birthday

## Automations

Example automation to send a reminder message every Friday:

```yaml
automation:
  - alias: "Weekly Allowance Reminder"
    trigger:
      - platform: time
        at: "18:00:00"
      - platform: time_pattern
        weekday: "5"  # Friday
    action:
      - service: notify.mobile_app
        data:
          title: "Weekly Allowance Reminder"
          message: >
            Time to give allowances:
            {% for entity_id in states.sensor | selectattr('entity_id', 'search', '_allowance') | map(attribute='entity_id') %}
              {{ states[entity_id].name }}: {{ states[entity_id].attributes.formatted_value }}
            {% endfor %}
```

## Troubleshooting

### Common Issues

- **Invalid Date Error**: Make sure the birthday is in the format `YYYY-MM-DD`
- **Sensors Not Updating**: The sensors update at midnight each day. To force an update, restart Home Assistant
- **Integration Not Found**: Make sure you've correctly installed the component and restarted Home Assistant

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the Home Assistant community for inspiration and support

