# Order of masks is important !
NOFOLLOW_MASKS = [
    (4, "robots"),
    (2, "meta"),
    (1, "link"),
]


def follow_mask(val):
    """
    In raw files, an url can be at the same time as "robots_no_follow" and "meta_no_follow"
    We return a concatenated version
    """
    _mask = int(val)
    if _mask in (0, 8):
        return ["follow"]
    masks = []
    for bitmask, term in NOFOLLOW_MASKS:
        if bitmask & _mask == bitmask:
            masks.append(term)
    return masks


def list_to_mask(lst):
    mask = 0
    if lst == ['follow']:
        return 0
    for mask_int, mask_name in NOFOLLOW_MASKS:
        if mask_name in lst:
            mask += mask_int
    return mask