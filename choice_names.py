def _build_discriminator_choices(self) -> None:
    # Note: Currently, including a discriminator in a choice means that it
    # will have a fixed count, ie. you can select it or not select but you can't
    # get more or less of it. This will be fixed later when choices are made
    # more flexible.

    # TODO: Revisit code here when choices with variable counts are added
    for group in discriminators.choice_groups(self.products, self.ix,
                                              self.defs['binary_choices']):
        if len(group) < 2: continue
        # Remove None if present
        group = {g for g in group if g is not None}
        for option in group:
            if option and option not in self.choice_names:
                raise ValueError(
                    "No choice name for discriminator %s in %s. Consider adding one to "
                    "choice_names.tsv" % (option, group))
        names = {self.choice_names[option] for option in group if option}
        name = more_itertools.one(
            names,
            too_long=ValueError(
                "Multiple choice names %s for discriminators %s" % (names, group)))
        assert name not in self.named_choices, (name, group)
        self.named_choices[name].update(group)