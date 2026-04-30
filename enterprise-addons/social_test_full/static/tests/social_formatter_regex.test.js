import { expect, test } from "@odoo/hoot";
import { markup } from "@odoo/owl";

import { patchWithCleanup } from "@web/../tests/web_test_helpers";

import { SocialPostFormatterMixinBase } from "@social/js/social_post_formatter_mixin";

const Markup = markup("").constructor;

test("Facebook Message", () => {
    patchWithCleanup(SocialPostFormatterMixinBase, {
        _getMediaType() {
            return "facebook";
        },
        _formatPost() {
            this.originalPost = { account_id: { raw_value: 42 } };
            return super._formatPost(...arguments);
        },
    });

    const testMessage =
        "Hello @[542132] Erp-Social, check this out: https://dev.erpsys.top?utm=mail&param=1,2,3 #crazydeals #odoo";
    const finalMessage = SocialPostFormatterMixinBase._formatPost(testMessage);

    expect(finalMessage.toString()).toEqual(
        [
            "Hello",
            "<a href='/social_facebook/redirect_to_profile/42/542132?name=Erp-Social' target='_blank'>Erp-Social</a>,",
            "check this out:",
            "<a href='https://dev.erpsys.top?utm=mail&amp;param=1,2,3' class='text-truncate' target='_blank' rel='noreferrer noopener'>https://dev.erpsys.top?utm=mail&amp;param=1,2,3</a>",
            "<a href='https://www.facebook.com/hashtag/crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.facebook.com/hashtag/odoo' target='_blank'>#odoo</a>",
        ].join(" ")
    );
    expect(finalMessage).toBeInstanceOf(Markup);
});

test("Instagram Message", () => {
    patchWithCleanup(SocialPostFormatterMixinBase, {
        _getMediaType() {
            return "instagram";
        },
    });

    const testMessage =
        "Hello @Erp.Social, check this out: https://dev.erpsys.top #crazydeals #odoo";
    const finalMessage = SocialPostFormatterMixinBase._formatPost(testMessage);

    expect(finalMessage.toString()).toEqual(
        [
            "Hello",
            "<a href='https://www.instagram.com/Erp.Social' target='_blank'>@Erp.Social</a>,",
            "check this out:",
            "<a href='https://dev.erpsys.top' class='text-truncate' target='_blank' rel='noreferrer noopener'>https://dev.erpsys.top</a>",
            "<a href='https://www.instagram.com/explore/tags/crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.instagram.com/explore/tags/odoo' target='_blank'>#odoo</a>",
        ].join(" ")
    );
    expect(finalMessage).toBeInstanceOf(Markup);
});

test("LinkedIn Message", () => {
    patchWithCleanup(SocialPostFormatterMixinBase, {
        _getMediaType() {
            return "linkedin";
        },
    });

    const testMessage = "Hello, check this out: https://dev.erpsys.top {hashtag|#|crazydeals} #odoo";
    const finalMessage = SocialPostFormatterMixinBase._formatPost(testMessage);

    expect(finalMessage.toString()).toEqual(
        [
            "Hello, check this out:",
            "<a href='https://dev.erpsys.top' class='text-truncate' target='_blank' rel='noreferrer noopener'>https://dev.erpsys.top</a>",
            "<a href='https://www.linkedin.com/feed/hashtag/?keywords=crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.linkedin.com/feed/hashtag/?keywords=odoo' target='_blank'>#odoo</a>",
        ].join(" ")
    );
    expect(finalMessage).toBeInstanceOf(Markup);
});

test("Twitter Message", () => {
    patchWithCleanup(SocialPostFormatterMixinBase, {
        _getMediaType() {
            return "twitter";
        },
    });

    const testMessage =
        "Hello @Erp-Social, check this out: https://dev.erpsys.top #crazydeals #odoo";
    const finalMessage = SocialPostFormatterMixinBase._formatPost(testMessage);

    expect(finalMessage.toString()).toEqual(
        [
            "Hello",
            "<a href='https://twitter.com/Erp-Social' target='_blank'>@Erp-Social</a>,",
            "check this out:",
            "<a href='https://dev.erpsys.top' class='text-truncate' target='_blank' rel='noreferrer noopener'>https://dev.erpsys.top</a>",
            "<a href='https://twitter.com/hashtag/crazydeals?src=hash' target='_blank'>#crazydeals</a>",
            "<a href='https://twitter.com/hashtag/odoo?src=hash' target='_blank'>#odoo</a>",
        ].join(" ")
    );
    expect(finalMessage).toBeInstanceOf(Markup);
});

test("YouTube Message", () => {
    patchWithCleanup(SocialPostFormatterMixinBase, {
        _getMediaType() {
            return "youtube";
        },
    });

    const testMessage = "Hello, check this out: https://dev.erpsys.top #crazydeals #odoo";
    const finalMessage = SocialPostFormatterMixinBase._formatPost(testMessage);

    expect(finalMessage.toString()).toEqual(
        [
            "Hello, check this out:",
            "<a href='https://dev.erpsys.top' class='text-truncate' target='_blank' rel='noreferrer noopener'>https://dev.erpsys.top</a>",
            "<a href='https://www.youtube.com/results?search_query=%23crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.youtube.com/results?search_query=%23odoo' target='_blank'>#odoo</a>",
        ].join(" ")
    );
    expect(finalMessage).toBeInstanceOf(Markup);
});

test("URL regex supports special characters across all media types", () => {
    const mediaTypes = ['facebook', 'instagram', 'linkedin', 'twitter', 'youtube'];
    const testUrl = 'https://example.com/path(v1)/search?tags=$web,mobile*&price=$100';
    const testMessage = `Check this URL: ${testUrl} #test`;
    const testUrlNoAnd = testUrl.replace(/&/g, '&amp;');

    expect.assertions(mediaTypes.length);

    mediaTypes.forEach(mediaType => {
        patchWithCleanup(SocialPostFormatterMixinBase, {
            _getMediaType() { return mediaType; },
        });

        const finalMessage = SocialPostFormatterMixinBase._formatPost(testMessage);
        const expectedUrlPattern = `<a href='${testUrlNoAnd}' class='text-truncate' target='_blank' rel='noreferrer noopener'>${testUrlNoAnd}</a>`;

        expect(finalMessage.includes(expectedUrlPattern)).toBe(
            true,
            { message: `URL with special characters (parentheses, asterisk, dollar sign, comma, apostrophe) should be properly formatted for ${mediaType}` }
        );
    });
});
