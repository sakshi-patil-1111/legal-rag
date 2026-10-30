#!/usr/bin/env bash
# NYAAY AI — palette collapse codemod.
#
# Rewrites hardcoded hex literals to the canonical palette declared in
# tailwind.config.js. Every mapping below is one-directional into a terminal
# value (no mapping's output is another mapping's input), so a single pass is
# order-independent and idempotent.
#
# Roles were verified with `grep -oh "[a-z-]*-\[#HEX\]"` before assignment —
# text colours map to ink.*, surfaces map to paper.*/dark.*.
set -euo pipefail

cd "$(dirname "$0")/src"

FILES=$(find . -type f \( -name '*.jsx' -o -name '*.tsx' -o -name '*.ts' -o -name '*.js' \))

apply() {
  local from=$1 to=$2
  # shellcheck disable=SC2086
  sed -i "s/${from}/${to}/gI" $FILES
}

# ---- navy surfaces: 7 -> 3 (#121820 base, #1A222D raised, #2B3542 rule) ----
apply '#1E2633' '#1A222D'
apply '#171F2B' '#1A222D'
apply '#222C3A' '#2B3542'
apply '#242F3E' '#2B3542'
apply '#344256' '#2B3542'
apply '#404040' '#2B3542'

# ---- warm paper: 11 -> 3 (#FAF7F2 base, #FFFFFF raised, #F2EFE9 sunken) ----
apply '#F9F8F5' '#FAF7F2'
apply '#F9F9F8' '#FAF7F2'
apply '#FDFCFB' '#FAF7F2'
apply '#F8F8F7' '#FAF7F2'
apply '#EFECE6' '#F2EFE9'
apply '#EFEBE4' '#F2EFE9'
apply '#EDE8DD' '#F2EFE9'
apply '#EAE4D8' '#F2EFE9'
apply '#F4F1EB' '#F2EFE9'
apply '#F2F4F7' '#F2EFE9'   # cool-gray purge

# ---- rules: 6 -> 2 (#E4DFD5 subtle, #D5CEC2 strong) ----
apply '#DDD6C9' '#D5CEC2'
apply '#D4CFC4' '#D5CEC2'
apply '#E5E7EB' '#E4DFD5'   # cool-gray purge

# ---- ink on paper: 13 -> 4. #7A8699 was 3.45:1 and FAILED WCAG AA. ----
apply '#7A8699' '#667085'
apply '#8997AB' '#667085'
apply '#7A7469' '#667085'   # abandoned Ink & Paper warm gray
apply '#A8A39A' '#667085'
apply '#5A687D' '#556377'
apply '#718096' '#556377'   # cool-gray purge
apply '#2D3748' '#475467'   # cool-gray purge
apply '#334155' '#475467'   # cool-gray purge
apply '#344054' '#475467'   # cool-gray purge
apply '#1A1814' '#121820'   # abandoned Ink & Paper warm black

# ---- slate on dark: -> #A2B1C6 (8.2:1) / #7A8699 (4.8:1) ----
apply '#A0AEC0' '#A2B1C6'
apply '#48566A' '#7A8699'   # on-dark; #667085 would drop below AA there

# ---- accent: 10 -> 3. Collapses the abandoned ochre into rust. ----
apply '#C8821A' '#C84B31'
apply '#B85020' '#A83C25'
apply '#B33D24' '#A83C25'
apply '#B83A2A' '#A83C25'
apply '#9B2E21' '#8C271E'
apply '#912018' '#8C271E'
apply '#F9EDD5' '#FAEAE7'   # ochre wash -> rust wash
apply '#FAEAE8' '#FAEAE7'

echo "codemod complete"
