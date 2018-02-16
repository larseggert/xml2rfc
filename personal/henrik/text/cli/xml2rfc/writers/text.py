# Copyright The IETF Trust 2018, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import datetime

from codecs import open
from lxml import etree

try:
    import debug
    debug.debug = True
except ImportError:
    pass


from xml2rfc import log
from xml2rfc.writers.base import default_options
from xml2rfc import utils


fill = utils.TextWrapper(width=69, fix_sentence_endings=True, break_on_hyphens=False).fill
seen = set()

class TextWriter:

    def __init__(self, xmlrfc, quiet=None, options=default_options, date=datetime.date.today()):
        self.xmlrfc = xmlrfc
        self.tree = xmlrfc.tree
        self.root = self.tree.getroot()
        self.options = options
        self.errors = []

    def write(self, filename):
        """ Public method to write the XML document to a file """

        text = self.render()
        if self.errors:
            log.write("Not creating output file due to errors (see above)")
            return

        # Use lxml's built-in serialization
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)

        if not self.options.quiet:
            log.write('Created file', filename)

    def render(self, e=None, **kwargs):
        if isinstance(e, etree._Comment):
            return ''
        e = self.root if e is None else e
        func_name = "render_%s" % (e.tag,)
        func = getattr(self, func_name, self.default_renderer)
        if func == self.default_renderer:
            if not e.tag in seen:
                log.warn("No renderer for <%s> found" % (e.tag, ))
                seen.add(e.tag)
        return func(e, **kwargs)

    def element(self, tag, **kwargs):
        return etree.Element(tag, **kwargs)

    # --- fallback rendering functions ------------------------------------------

    def default_renderer(self, e, **kwargs):
        # This is a fallback when a more specific function doesn't exist
        text = "<%s>:%s" % (e.tag, e.text or '')
        for c in e.getchildren():
            ctext = self.render(c, **kwargs)
            if isinstance(ctext, list):
                ctext = "\n\n".join(ctext)
            if ctext is None:
                debug.show('e')
                debug.show('c')
            text += '\n' + ctext
        text += e.tail or ''
        return text

    def parts_renderer(self, e, **kwargs):
        parts = []
        for c in e.getchildren():
            ctext = self.render(c, **kwargs)
            if isinstance(ctext, list):
                parts += ctext
            else:
                parts.append(ctext)
        return parts

    def inner_text_renderer(self, e, **kwargs):
        text = e.text or ''
        for c in e.getchildren():
            text += self.render(c, **kwargs)
        return text
    
    def text_renderer(self, e, **kwargs):
        text = self.inner_text_renderer(e, **kwargs)
        text += e.tail
        return text

    # --- element rendering functions ------------------------------------------

    def render_rfc(self, e, paginated=False, **kwargs):
        parts = []
        for c in e.getchildren():
            ctext = self.render(c, **kwargs)
            if isinstance(ctext, list):
                parts += ctext
            else:
                parts.append(ctext)
        if paginated:
            text = self.page_join(parts)
        else:
            for part in parts:
                if isinstance(part, tuple):
                    debug.show('part')
            text = "\n\n".join(parts)
        return text

    def render_link(self, e, **kwargs):
        return ''

    def render_front(self, e, **kwargs):
        return self.parts_renderer(e, **kwargs)








#    def render_email(self, e, **kwargs):
#    def render_eref(self, e, **kwargs):
#    def render_facsimile(self, e, **kwargs):
#    def render_figure(self, e, **kwargs):
#    def render_format(self, e, **kwargs):
#    def render_iref(self, e, **kwargs):
#    def render_keyword(self, e, **kwargs):
#    def render_li(self, e, **kwargs):
#    def render_list(self, e, **kwargs):
#    def render_note(self, e, **kwargs):
#    def render_ol(self, e, **kwargs):
#    def render_organization(self, e, **kwargs):
#    def render_phone(self, e, **kwargs):
#    def render_postal(self, e, **kwargs):
#    def render_postalLine(self, e, **kwargs):
#    def render_postamble(self, e, **kwargs):
#    def render_preamble(self, e, **kwargs):
#    def render_refcontent(self, e, **kwargs):
#    def render_reference(self, e, **kwargs):
#    def render_referencegroup(self, e, **kwargs):
#    def render_references(self, e, **kwargs):
#    def render_region(self, e, **kwargs):
#    def render_relref(self, e, **kwargs):
#    def render_seriesInfo(self, e, **kwargs):
#    def render_sourcecode(self, e, **kwargs):
#    def render_spanx(self, e, **kwargs):
#    def render_street(self, e, **kwargs):
#    def render_strong(self, e, **kwargs):
#    def render_sub(self, e, **kwargs):
#    def render_sup(self, e, **kwargs):
#    def render_table(self, e, **kwargs):
#    def render_tbody(self, e, **kwargs):
#    def render_td(self, e, **kwargs):
#    def render_texttable(self, e, **kwargs):
#    def render_tfoot(self, e, **kwargs):
#    def render_th(self, e, **kwargs):
#    def render_thead(self, e, **kwargs):
#    def render_title(self, e, **kwargs):
#    def render_tr(self, e, **kwargs):
#    def render_tt(self, e, **kwargs):
#    def render_ttcol(self, e, **kwargs):
#    def render_ul(self, e, **kwargs):
#    def render_uri(self, e, **kwargs):
#    def render_vspace(self, e, **kwargs):
#    def render_workgroup(self, e, **kwargs):
#    def render_xref(self, e, **kwargs):

    def render_middle(self, e, **kwargs):
        return self.parts_renderer(e, **kwargs)

    def render_section(self, e, **kwargs):
        parts = []
        kwargs.update(e.items())
        pn = kwargs['pn']
        num = pn.split('-')[1].capitalize()
        children = e.getchildren()
        if children[0].tag == 'name':
            name = children[0]
            children = children[1:]
            title = "%s.  %s" % (num, self.render(name, label=None, **kwargs))
        else:
            title = "%s." % (num, )
        parts.append(title)
        for c in children:
            ctext = self.render(c, **kwargs)
            if isinstance(ctext, list):
                parts += ctext
            else:
                parts.append(ctext)
        return parts

    def render_name(self, e, label=None, pn=None, **kwargs):
        return self.inner_text_renderer(e, **kwargs).strip()

#    def render_t(self, e, **kwargs):
    def render_t(self, e, indent=3, **kwargs):
        text = self.inner_text_renderer(e, **kwargs)
        text = fill(text, initial=' '*indent)
        return text

    def render_figure(self, e, **kwargs):
        parts = []
        kwargs.update(e.items())
        pn = kwargs['pn']
        num = pn.split('-')[1].capitalize()
        children = e.getchildren()
        if children[0].tag == 'name':
            name = children[0]
            children = children[1:]
            title = "Figure %s: %s" % (num, self.render(name, label=None, **kwargs))
        else:
            title = "Figure %s" % (num, )
        for c in children:
            ctext = self.render(c, indent=0, **kwargs)
            if isinstance(ctext, list):
                parts += ctext
            else:
                parts.append(ctext)
        parts.append('   '+title.center(69).rstrip())
        return parts





    # 2.1.  <abstract>
    # 
    #    Contains the Abstract of the document.  See [RFC7322] for more
    #    information on restrictions for the Abstract.
    #
    #    This element appears as a child element of <front> (Section 2.26).
    # 
    # ...
    # 
    # 2.1.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the Abstract.
#    def render_abstract(self, e, **kwargs):

    # 2.2.  <address>
    # 
    #    Provides address information for the author.
    # 
    #    This element appears as a child element of <author> (Section 2.7).
#    def render_address(self, e, **kwargs):

    # 2.3.  <annotation>
    # 
    #    Provides additional prose augmenting a bibliographic reference.  This
    #    text is intended to be shown after the rest of the generated
    #    reference text.
    # 
    #    This element appears as a child element of <reference>
    #    (Section 2.40).
#    def render_annotation(self, e, **kwargs):


    # 2.4.  <area>
    # 
    #    Provides information about the IETF area to which this document
    #    relates (currently not used when generating documents).
    # 
    #    The value ought to be either the full name or the abbreviation of one
    #    of the IETF areas as listed on <http://www.ietf.org/iesg/area.html>.
    #    A list of full names and abbreviations will be kept by the RFC Series
    #    Editor.
    # 
    #    This element appears as a child element of <front> (Section 2.26).
#    def render_area(self, e, **kwargs):


    # 2.5.  <artwork>
    # 
    #    This element allows the inclusion of "artwork" in the document.
    #    <artwork> provides full control of horizontal whitespace and line
    #    breaks; thus, it is used for a variety of things, such as diagrams
    #    ("line art") and protocol unit diagrams.  Tab characters (U+0009)
    #    inside of this element are prohibited.
    # 
    #    Alternatively, the "src" attribute allows referencing an external
    #    graphics file, such as a vector drawing in SVG or a bitmap graphic
    #    file, using a URI.  In this case, the textual content acts as a
    #    fallback for output representations that do not support graphics;
    #    thus, it ought to contain either (1) a "line art" variant of the
    #    graphics or (2) prose that describes the included image in sufficient
    #    detail.
    # 
    #    In [RFC7749], the <artwork> element was also used for source code and
    #    formal languages; in v3, this is now done with <sourcecode>.
    # 
    #    There are at least five ways to include SVG in artwork in
    #    Internet-Drafts:
    # 
    #    o  Inline, by including all of the SVG in the content of the element,
    #       such as: <artwork type="svg"><svg xmlns="http://www.w3.org/2000/
    #       svg...">
    # 
    #    o  Inline, but using XInclude (see Appendix B.1), such as: <artwork
    #       type="svg"><xi:include href=...>
    # 
    #    o  As a data: URI, such as: <artwork type="svg" src="data:image/
    #       svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3...">
    # 
    #    o  As a URI to an external entity, such as: <artwork type="svg"
    #       src="http://www.example.com/...">
    # 
    #    o  As a local file, such as: <artwork type="svg" src="diagram12.svg">
    # 
    #    The use of SVG in Internet-Drafts and RFCs is covered in much more
    #    detail in [RFC7996].
    # 
    #    The above methods for inclusion of SVG art can also be used for
    #    including text artwork, but using a data: URI is probably confusing
    #    for text artwork.
    # 
    #    Formatters that do pagination should attempt to keep artwork on a
    #    single page.  This is to prevent artwork that is split across pages
    #    from looking like two separate pieces of artwork.
    # 
    #    See Section 5 for a description of how to deal with issues of using
    #    "&" and "<" characters in artwork.
#    def render_artwork(self, e, **kwargs):


    # 2.5.1.  "align" Attribute
    # 
    #    Controls whether the artwork appears left justified (default),
    #    centered, or right justified.  Artwork is aligned relative to the
    #    left margin of the document.
    # 
    #    Allowed values:
    # 
    #    o  "left" (default)
    # 
    #    o  "center"
    # 
    #    o  "right"


    # 2.5.2.  "alt" Attribute
    # 
    #    Alternative text description of the artwork (which is more than just
    #    a summary or caption).  When the art comes from the "src" attribute
    #    and the format of that artwork supports alternate text, the
    #    alternative text comes from the text of the artwork itself, not from
    #    this attribute.  The contents of this attribute are important to
    #    readers who are visually impaired, as well as those reading on
    #    devices that cannot show the artwork well, or at all.


    # 2.5.3.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this artwork.

    # 2.5.5.  "name" Attribute
    # 
    #    A filename suitable for the contents (such as for extraction to a
    #    local file).  This attribute can be helpful for other kinds of tools
    #    (such as automated syntax checkers, which work by extracting the
    #    artwork).  Note that the "name" attribute does not need to be unique
    #    for <artwork> elements in a document.  If multiple <artwork> elements
    #    have the same "name" attribute, a processing tool might assume that
    #    the elements are all fragments of a single file, and the tool can
    #    collect those fragments for later processing.  See Section 7 for a
    #    discussion of possible problems with the value of this attribute.

    # 2.5.6.  "src" Attribute
    # 
    #    The URI reference of a graphics file [RFC3986], or the name of a file
    #    on the local disk.  This can be a "data" URI [RFC2397] that contains
    #    the contents of the graphics file.  Note that the inclusion of art
    #    with the "src" attribute depends on the capabilities of the
    #    processing tool reading the XML document.  Tools need to be able to
    #    handle the file: URI, and they should be able to handle http: and
    #    https: URIs as well.  The prep tool will be able to handle reading
    #    the "src" attribute.
    # 
    #    If no URI scheme is given in the attribute, the attribute is
    #    considered to be a local filename relative to the current directory.
    #    Processing tools must be careful to not accept dangerous values for
    #    the filename, particularly those that contain absolute references
    #    outside the current directory.  Document creators should think hard
    #    before using relative URIs due to possible later problems if files
    #    move around on the disk.  Also, documents should most likely use
    #    explicit URI schemes wherever possible.
    # 
    #    In some cases, the prep tool may remove the "src" attribute after
    #    processing its value.  See [RFC7998] for a description of this.
    # 
    #    It is an error to have both a "src" attribute and content in the
    #    <artwork> element.

    # 2.5.7.  "type" Attribute
    # 
    #    Specifies the type of the artwork.  The value of this attribute is
    #    free text with certain values designated as preferred.
    # 
    #    The preferred values for <artwork> types are:
    # 
    #    o  ascii-art
    # 
    #    o  binary-art
    # 
    #    o  call-flow
    # 
    #    o  hex-dump
    # 
    #    o  svg
    # 
    #    The RFC Series Editor will maintain a complete list of the preferred
    #    values on the RFC Editor web site, and that list is expected to be
    #    updated over time.  Thus, a consumer of v3 XML should not cause a
    #    failure when it encounters an unexpected type or no type is
    #    specified.  The table will also indicate which type of art can appear
    #    in plain-text output (for example, type="svg" cannot).



    # 2.6.  <aside>
    # 
    #    This element is a container for content that is semantically less
    #    important or tangential to the content that surrounds it.
    # 
    #    This element appears as a child element of <section> (Section 2.46).
    #
    # 2.6.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this aside.
#    def render_aside(self, e, **kwargs):


    # 2.7.  <author>
    # 
    #    Provides information about a document's author.  This is used both
    #    for the document itself (at the beginning of the document) and for
    #    referenced documents.
    # 
    #    The <author> elements contained within the document's <front> element
    #    are used to fill the boilerplate and also to generate the "Author's
    #    Address" section (see [RFC7322]).
    # 
    #    Note that an "author" can also be just an organization (by not
    #    specifying any of the "name" attributes, but adding the
    #    <organization> child element).
    # 
    #    Furthermore, the "role" attribute can be used to mark an author as
    #    "editor".  This is reflected both on the front page and in the
    #    "Author's Address" section, as well as in bibliographic references.
    #    Note that this specification does not define a precise meaning for
    #    the term "editor".
    # 
    #    This element appears as a child element of <front> (Section 2.26).
    # 
    # ...
    # 
    # 2.7.1.  "asciiFullname" Attribute
    # 
    #    The ASCII equivalent of the author's full name.
    # 
    # 2.7.2.  "asciiInitials" Attribute
    # 
    #    The ASCII equivalent of the author's initials, to be used in
    #    conjunction with the separately specified asciiSurname.
    # 
    # 2.7.3.  "asciiSurname" Attribute
    # 
    #    The ASCII equivalent of the author's surname, to be used in
    #    conjunction with the separately specified asciiInitials.
    # 
    # 2.7.4.  "fullname" Attribute
    # 
    #    The full name (used in the automatically generated "Author's Address"
    #    section).  Although this attribute is optional, if one or more of the
    #    "asciiFullname", "asciiInitials", or "asciiSurname" attributes have
    #    values, the "fullname" attribute is required.
    # 
    # 2.7.5.  "initials" Attribute
    # 
    #    An abbreviated variant of the given name(s), to be used in
    #    conjunction with the separately specified surname.  It usually
    #    appears on the front page, in footers, and in references.
    # 
    #    Some processors will post-process the value -- for instance, when it
    #    only contains a single letter (in which case they might add a
    #    trailing dot).  Relying on this kind of post-processing can lead to
    #    results varying across formatters and thus ought to be avoided.
    # 
    # 2.7.6.  "role" Attribute
    # 
    #    Specifies the role the author had in creating the document.
    # 
    #    Allowed value:
    # 
    #    o  "editor"
    # 
    # 2.7.7.  "surname" Attribute
    # 
    #    The author's surname, to be used in conjunction with the separately
    #    specified initials.  It usually appears on the front page, in
    #    footers, and in references.
#    def render_author(self, e, **kwargs):


    # 2.8.  <back>
    # 
    #    Contains the "back" part of the document: the references and
    #    appendices.  In <back>, <section> elements indicate appendices.
    # 
    #    This element appears as a child element of <rfc> (Section 2.45).
    def render_back(self, e, **kwargs):
        return self.parts_renderer(e, **kwargs)


    # 2.9.  <bcp14>
    # 
    #    Marks text that are phrases defined in [BCP14] such as "MUST",
    #    "SHOULD NOT", and so on.  When shown in some of the output
    #    representations, the text in this element might be highlighted.  The
    #    use of this element is optional.
    # 
    #    This element is only to be used around the actual phrase from BCP 14,
    #    not the full definition of a requirement.  For example, it is correct
    #    to say "The packet <bcp14>MUST</bcp14> be dropped.", but it is not
    #    correct to say "<bcp14>The packet MUST be dropped.</bcp14>".
    # 
    #    This element appears as a child element of <annotation>
    #    (Section 2.3), <blockquote> (Section 2.10), <dd> (Section 2.18), <dt>
    #    (Section 2.21), <em> (Section 2.22), <li> (Section 2.29), <preamble>
    #    (Section 3.6), <refcontent> (Section 2.39), <strong> (Section 2.50),
    #    <sub> (Section 2.51), <sup> (Section 2.52), <t> (Section 2.53), <td>
    #    (Section 2.56), <th> (Section 2.58), and <tt> (Section 2.62).
    # 
    #    Content model: only text content.
#    def render_bcp14(self, e, **kwargs):


    # 2.10.  <blockquote>
    # 
    #    Specifies that a block of text is a quotation.
    # 
    #    This element appears as a child element of <section> (Section 2.46).
    # 
    # 2.10.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this quotation.
    # 
    # 2.10.2.  "cite" Attribute
    # 
    #    The source of the citation.  This must be a URI.  If the "quotedFrom"
    #    attribute is given, this URI will be used by processing tools as the
    #    link for the text of that attribute.
    # 
    # 2.10.3.  "quotedFrom" Attribute
    # 
    #    Name of person or document the text in this element is quoted from.
    #    A formatter should render this as visible text at the end of the
    #    quotation.
#    def render_blockquote(self, e, **kwargs):


    # 2.11.  <boilerplate>
    # 
    #    Holds the boilerplate text for the document.  This element is filled
    #    in by the prep tool.
    # 
    #    This element contains <section> elements.  Every <section> element in
    #    this element must have the "numbered" attribute set to "false".
    # 
    #    This element appears as a child element of <front> (Section 2.26).
    def render_boilerplate(self, e, **kwargs):
        assert kwargs.get('numbered') == 'false'
        return self.render_section(e, **kwargs)


    # 2.12.  <br>
    # 
    #    Indicates that a line break should be inserted in the generated
    #    output by a formatting tool.  Multiple successive instances of this
    #    element are ignored.
    # 
    #    This element appears as a child element of <td> (Section 2.56) and
    #    <th> (Section 2.58).
#    def render_br(self, e, **kwargs):


    # 2.13.  <city>
    # 
    #    Gives the city name in a postal address.
    # 
    #    This element appears as a child element of <postal> (Section 2.37).
    # 
    # 2.13.1.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the city name.
#    def render_city(self, e, **kwargs):


    # 2.14.  <code>
    # 
    #    Gives the postal region code.
    # 
    #    This element appears as a child element of <postal> (Section 2.37).
    # 
    # 2.14.1.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the postal code.
#    def render_code(self, e, **kwargs):


    # 2.15.  <country>
    # 
    #    Gives the country name or code in a postal address.
    # 
    #    This element appears as a child element of <postal> (Section 2.37).
    # 
    # 2.15.1.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the country name.
#    def render_country(self, e, **kwargs):


    # 2.16.  <cref>
    # 
    #    Represents a comment.
    # 
    #    Comments can be used in a document while it is work in progress.
    #    They might appear either inline and visually highlighted, at the end
    #    of the document, or not at all, depending on the formatting tool.
    # 
    #    This element appears as a child element of <annotation>
    #    (Section 2.3), <blockquote> (Section 2.10), <c> (Section 3.1), <dd>
    #    (Section 2.18), <dt> (Section 2.21), <em> (Section 2.22), <li>
    #    (Section 2.29), <name> (Section 2.32), <postamble> (Section 3.5),
    #    <preamble> (Section 3.6), <strong> (Section 2.50), <sub>
    #    (Section 2.51), <sup> (Section 2.52), <t> (Section 2.53), <td>
    #    (Section 2.56), <th> (Section 2.58), <tt> (Section 2.62), and <ttcol>
    #    (Section 3.9).
    # 
    # 2.16.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this comment.
    # 
    # 2.16.2.  "display" Attribute
    # 
    #    Suggests whether or not the comment should be displayed by formatting
    #    tools.  This might be set to "false" if you want to keep a comment in
    #    a document after the contents of the comment have already been dealt
    #    with.
    # 
    #    Allowed values:
    # 
    #    o  "true" (default)
    # 
    #    o  "false"
    # 
    # 2.16.3.  "source" Attribute
    # 
    #    Holds the "source" of a comment, such as the name or the initials of
    #    the person who made the comment.
#    def render_cref(self, e, **kwargs):


    # 2.17.  <date>
    # 
    #    Provides information about the publication date.  This element is
    #    used for two cases: the boilerplate of the document being produced,
    #    and inside bibliographic references that use the <front> element.
    # 
    #    Boilerplate for Internet-Drafts and RFCs:  This element defines the
    #       date of publication for the current document (Internet-Draft or
    #       RFC).  When producing Internet-Drafts, the prep tool uses this
    #       date to compute the expiration date (see [IDGUIDE]).  When one or
    #       more of "year", "month", or "day" are left out, the prep tool will
    #       attempt to use the current system date if the attributes that are
    #       present are consistent with that date.
    # 
    #       In dates in <rfc> elements, the month must be a number or a month
    #       in English.  The prep tool will silently change text month names
    #       to numbers.  Similarly, the year must be a four-digit number.
    # 
    #       When the prep tool is used to create Internet-Drafts, it will
    #       reject a submitted Internet-Draft that has a <date> element in the
    #       boilerplate for itself that is anything other than today.  That
    #       is, the tool will not allow a submitter to specify a date other
    #       than the day of submission.  To avoid this problem, authors might
    #       simply not include a <date> element in the boilerplate.
    # 
    #    Bibliographic references:  In dates in <reference> elements, the date
    #       information can have prose text for the month or year.  For
    #       example, vague dates (year="ca. 2000"), date ranges
    #       (year="2012-2013"), non-specific months (month="Second quarter"),
    #       and so on are allowed.
    # 
    #    This element appears as a child element of <front> (Section 2.26).
    # 
    # 2.17.1.  "day" Attribute
    # 
    #    The day of publication.
    # 
    # 2.17.2.  "month" Attribute
    # 
    #    The month or months of publication.
    # 
    # 2.17.3.  "year" Attribute
    # 
    #    The year or years of publication.
#    def render_date(self, e, **kwargs):


    # 2.18.  <dd>
    # 
    #    The definition part of an entry in a definition list.
    # 
    #    This element appears as a child element of <dl> (Section 2.20).
    # 
    # 2.18.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this definition.
#    def render_dd(self, e, **kwargs):


    # 2.19.  <displayreference>
    # 
    #    This element gives a mapping between the anchor of a reference and a
    #    name that will be displayed instead.  This allows authors to display
    #    more mnemonic anchor names for automatically included references.
    #    The mapping in this element only applies to <xref> elements whose
    #    format is "default".  For example, if the reference uses the anchor
    #    "RFC6949", the following would cause that anchor in the body of
    #    displayed documents to be "RFC-dev":
    # 
    #    <displayreference target="RFC6949" to="RFC-dev"/>
    # 
    #    If a reference section is sorted, this element changes the sort
    #    order.
    # 
    #    It is expected that this element will only be valid in input
    #    documents.  It will likely be removed by prep tools when preparing a
    #    final version after those tools have replaced all of the associated
    #    anchors, targets, and "derivedContent" attributes.
    # 
    #    This element appears as a child element of <back> (Section 2.8).
    # 
    # 2.19.1.  "target" Attribute (Mandatory)
    # 
    #    This attribute must be the name of an anchor in a <reference> or
    #    <referencegroup> element.
    # 
    # 2.19.2.  "to" Attribute (Mandatory)
    # 
    #    This attribute is a name that will be displayed as the anchor instead
    #    of the anchor that is given in the <reference> element.  The string
    #    given must start with one of the following characters: 0-9, a-z, or
    #    A-Z.  The other characters in the string must be 0-9, a-z, A-Z, "-",
    #    ".", or "_".
    def render_displayreference(self, e, **kwargs):
        return ''


    # 2.20.  <dl>
    # 
    #    A definition list.  Each entry has a pair of elements: a term (<dt>)
    #    and a definition (<dd>).  (This is slightly different and simpler
    #    than the model used in HTML, which allows for multiple terms for a
    #    single definition.)
    # 
    #    This element appears as a child element of <abstract> (Section 2.1),
    #    <aside> (Section 2.6), <blockquote> (Section 2.10), <dd>
    #    (Section 2.18), <li> (Section 2.29), <note> (Section 2.33), <section>
    #    (Section 2.46), <td> (Section 2.56), and <th> (Section 2.58).
    # 
    # 2.20.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the list.
    # 
    # 2.20.2.  "hanging" Attribute
    # 
    #    The "hanging" attribute defines whether or not the term appears on
    #    the same line as the definition.  hanging="true" indicates that the
    #    term is to the left of the definition, while hanging="false"
    #    indicates that the term will be on a separate line.
    # 
    #    Allowed values:
    # 
    #    o  "false"
    # 
    #    o  "true" (default)
    # 
    # 2.20.3.  "spacing" Attribute
    # 
    #    Defines whether or not there is a blank line between entries.
    #    spacing="normal" indicates a single blank line, while
    #    spacing="compact" indicates no space between.
    # 
    #    Allowed values:
    # 
    #    o  "normal" (default)
    # 
    #    o  "compact"
#    def render_dl(self, e, **kwargs):


    # 2.21.  <dt>
    # 
    #    The term being defined in a definition list.
    # 
    #    This element appears as a child element of <dl> (Section 2.20).
    # 
    # 2.21.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this term.
#    def render_dt(self, e, **kwargs):


    # 2.22.  <em>
    # 
    #    Indicates text that is semantically emphasized.  Text enclosed within
    #    this element will be displayed as italic after processing.  This
    #    element can be combined with other character formatting elements, and
    #    the formatting will be additive.
    def render_em(self, e, **kwargs):
        # Render text with leading and trailing '_'
        text = '_%s_' % self.inside_text_renderer(e, **kwargs)
        text += e.tail
        return text

    # 2.23.  <email>
    # 
    #    Provides an email address.
    # 
    #    The value is expected to be the addr-spec defined in Section 2 of
    #    [RFC6068].
    # 
    #    This element appears as a child element of <address> (Section 2.2).
    # 
    #    Content model: only text content.
    # 
    # 2.23.1.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the author's email address.  This is only
    #    used if the email address has any internationalized components.
    # 
    # 2.24.  <eref>
    # 
    #    Represents an "external" link (as specified in the "target"
    #    attribute).  This is useful for embedding URIs in the body of a
    #    document.
    # 
    #    If the <eref> element has non-empty text content, formatters should
    #    use the content as the displayed text that is linked.  Otherwise, the
    #    formatter should use the value of the "target" attribute as the
    #    displayed text.  Formatters will link the displayed text to the value
    #    of the "target" attribute in a manner appropriate for the output
    #    format.
    # 
    #    For example, with an input of:
    # 
    #          This is described at
    #          <eref target="http://www.example.com/reports/r12.html"/>.
    # 
    #    An HTML formatter might generate:
    # 
    #          This is described at
    #          <a href="http://www.example.com/reports/r12.html">
    #          http://www.example.com/reports/r12.html</a>.
    # 
    #    With an input of:
    # 
    #          This is described
    #          <eref target="http://www.example.com/reports/r12.html">
    #          in this interesting report</eref>.
    # 
    #    An HTML formatter might generate:
    # 
    #          This is described
    #          <a href="http://www.example.com/reports/r12.html">
    #          in this interesting report</a>.
    # 
    #    This element appears as a child element of <annotation>
    #    (Section 2.3), <blockquote> (Section 2.10), <c> (Section 3.1), <cref>
    #    (Section 2.16), <dd> (Section 2.18), <dt> (Section 2.21), <em>
    #    (Section 2.22), <li> (Section 2.29), <name> (Section 2.32),
    #    <postamble> (Section 3.5), <preamble> (Section 3.6), <strong>
    #    (Section 2.50), <sub> (Section 2.51), <sup> (Section 2.52), <t>
    #    (Section 2.53), <td> (Section 2.56), <th> (Section 2.58), <tt>
    #    (Section 2.62), and <ttcol> (Section 3.9).
    # 
    #    Content model: only text content.
    # 
    # 2.24.1.  "target" Attribute (Mandatory)
    # 
    #    URI of the link target [RFC3986].  This must begin with a scheme name
    #    (such as "https://") and thus not be relative to the URL of the
    #    current document.
    # 
    # 2.25.  <figure>
    # 
    #    Contains a figure with a caption with the figure number.  If the
    #    element contains a <name> element, the caption will also show that
    #    name.
    # 
    #    This element appears as a child element of <aside> (Section 2.6),
    #    <blockquote> (Section 2.10), <dd> (Section 2.18), <li>
    #    (Section 2.29), <section> (Section 2.46), <td> (Section 2.56), and
    #    <th> (Section 2.58).
    # 
    #    Content model:
    # 
    #    In this order:
    # 
    #    1.  One optional <name> element (Section 2.32)
    # 
    #    2.  Optional <iref> elements (Section 2.27)
    # 
    #    3.  One optional <preamble> element (Section 3.6)
    # 
    #    4.  In any order, but at least one of:
    # 
    #        *  <artwork> elements (Section 2.5)
    # 
    #        *  <sourcecode> elements (Section 2.48)
    # 
    #    5.  One optional <postamble> element (Section 3.5)
    # 
    # 2.25.1.  "align" Attribute
    # 
    #    Deprecated.
    # 
    #    Note: does not affect title or <artwork> alignment.
    # 
    #    Allowed values:
    # 
    #    o  "left" (default)
    # 
    #    o  "center"
    # 
    #    o  "right"
    # 
    # 2.25.2.  "alt" Attribute
    # 
    #    Deprecated.  If the goal is to provide a single URI for a reference,
    #    use the "target" attribute in <reference> instead.
    # 
    # 2.25.3.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this figure.
    # 
    # 2.25.4.  "height" Attribute
    # 
    #    Deprecated.
    # 
    # 2.25.5.  "src" Attribute
    # 
    #    Deprecated.
    # 
    # 2.25.6.  "suppress-title" Attribute
    # 
    #    Deprecated.
    # 
    #    Allowed values:
    # 
    #    o  "true"
    # 
    #    o  "false" (default)
    # 
    # 2.25.7.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 2.25.8.  "width" Attribute
    # 
    #    Deprecated.
    # 
    # 2.26.  <front>
    # 
    #    Represents the "front matter": metadata (such as author information),
    #    the Abstract, and additional notes.
    # 
    #    A <front> element may have more than one <seriesInfo> element.  A
    #    <seriesInfo> element determines the document number (for RFCs) or
    #    name (for Internet-Drafts).  Another <seriesInfo> element determines
    #    the "maturity level" (defined in [RFC2026]), using values of "std"
    #    for "Standards Track", "bcp" for "BCP", "info" for "Informational",
    #    "exp" for "Experimental", and "historic" for "Historic".  The "name"
    #    attributes of those multiple <seriesInfo> elements interact as
    #    described in Section 2.47.
    # 
    #    This element appears as a child element of <reference> (Section 2.40)
    #    and <rfc> (Section 2.45).
    # 
    #    Content model:
    # 
    #    In this order:
    # 
    #    1.   One <title> element (Section 2.60)
    # 
    #    2.   Optional <seriesInfo> elements (Section 2.47)
    # 
    #    3.   One or more <author> elements (Section 2.7)
    # 
    #    4.   One optional <date> element (Section 2.17)
    # 
    #    5.   Optional <area> elements (Section 2.4)
    # 
    #    6.   Optional <workgroup> elements (Section 2.65)
    # 
    #    7.   Optional <keyword> elements (Section 2.28)
    # 
    #    8.   One optional <abstract> element (Section 2.1)
    # 
    #    9.   Optional <note> elements (Section 2.33)
    # 
    #    10.  One optional <boilerplate> element (Section 2.11)
    # 
    # 2.27.  <iref>
    # 
    #    Provides terms for the document's index.
    # 
    #    Index entries can be either regular entries (when just the "item"
    #    attribute is given) or nested entries (by specifying "subitem" as
    #    well), grouped under a regular entry.
    # 
    #    Index entries generally refer to the exact place where the <iref>
    #    element occurred.  An exception is the occurrence as a child element
    #    of <section>, in which case the whole section is considered to be
    #    relevant for that index entry.  In some formats, index entries of
    #    this type might be displayed as ranges.
    # 
    #    When the prep tool is creating index content, it collects the items
    #    in a case-sensitive fashion for both the item and subitem level.
    # 
    #    This element appears as a child element of <annotation>
    #    (Section 2.3), <aside> (Section 2.6), <blockquote> (Section 2.10),
    #    <c> (Section 3.1), <dd> (Section 2.18), <dt> (Section 2.21), <em>
    #    (Section 2.22), <figure> (Section 2.25), <li> (Section 2.29),
    #    <postamble> (Section 3.5), <preamble> (Section 3.6), <section>
    #    (Section 2.46), <strong> (Section 2.50), <sub> (Section 2.51), <sup>
    #    (Section 2.52), <t> (Section 2.53), <table> (Section 2.54), <td>
    #    (Section 2.56), <th> (Section 2.58), <tt> (Section 2.62), and <ttcol>
    #    (Section 3.9).
    # 
    #    Content model: this element does not have any contents.
    # 
    # 2.27.1.  "item" Attribute (Mandatory)
    # 
    #    The item to include.
    # 
    # 2.27.2.  "primary" Attribute
    # 
    #    Setting this to "true" declares the occurrence as "primary", which
    #    might cause it to be highlighted in the index.  There is no
    #    restriction on the number of occurrences that can be "primary".
    # 
    #    Allowed values:
    # 
    #    o  "true"
    # 
    #    o  "false" (default)
    # 
    # 2.27.3.  "subitem" Attribute
    # 
    #    The subitem to include.
    # 
    # 2.28.  <keyword>
    # 
    #    Specifies a keyword applicable to the document.
    # 
    #    Note that each element should only contain a single keyword; for
    #    multiple keywords, the element can simply be repeated.
    # 
    #    Keywords are used both in the RFC Index and in the metadata of
    #    generated document representations.
    # 
    #    This element appears as a child element of <front> (Section 2.26).
    # 
    #    Content model: only text content.
    # 
    # 2.29.  <li>
    # 
    #    A list element, used in <ol> and <ul>.
    # 
    #    This element appears as a child element of <ol> (Section 2.34) and
    #    <ul> (Section 2.63).
    # 
    #    Content model:
    # 
    #    Either:
    # 
    #       In any order, but at least one of:
    # 
    #       *  <artwork> elements (Section 2.5)
    # 
    #       *  <dl> elements (Section 2.20)
    # 
    #       *  <figure> elements (Section 2.25)
    # 
    #       *  <ol> elements (Section 2.34)
    # 
    #       *  <sourcecode> elements (Section 2.48)
    # 
    #       *  <t> elements (Section 2.53)
    # 
    #       *  <ul> elements (Section 2.63)
    # 
    #    Or:
    # 
    #       In any order, but at least one of:
    # 
    #       *  Text
    # 
    #       *  <bcp14> elements (Section 2.9)
    # 
    #       *  <cref> elements (Section 2.16)
    # 
    #       *  <em> elements (Section 2.22)
    # 
    #       *  <eref> elements (Section 2.24)
    # 
    #       *  <iref> elements (Section 2.27)
    # 
    #       *  <relref> elements (Section 2.44)
    # 
    #       *  <strong> elements (Section 2.50)
    # 
    #       *  <sub> elements (Section 2.51)
    # 
    #       *  <sup> elements (Section 2.52)
    # 
    #       *  <tt> elements (Section 2.62)
    # 
    #       *  <xref> elements (Section 2.66)
    # 
    # 2.29.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this list item.
    # 
    # 2.30.  <link>
    # 
    #    A link to an external document that is related to the RFC.
    # 
    #    The following are the supported types of external documents that can
    #    be pointed to in a <link> element:
    # 
    #    o  The current International Standard Serial Number (ISSN) for the
    #       RFC Series.  The value for the "rel" attribute is "item".  The
    #       link should use the form "urn:issn:".
    # 
    #    o  The Digital Object Identifier (DOI) for this document.  The value
    #       for the "rel" attribute is "describedBy".  The link should use the
    #       form specified in [RFC7669]; this is expected to change in the
    #       future.
    # 
    #    o  The Internet-Draft that was submitted to the RFC Editor to become
    #       the published RFC.  The value for the "rel" attribute is
    #       "convertedFrom".  The link should be to an IETF-controlled web
    #       site that retains copies of Internet-Drafts.
    # 
    #    o  A representation of the document offered by the document author.
    #       The value for the "rel" attribute is "alternate".  The link can be
    #       to a personally run web site.
    # 
    #    In RFC production mode, the prep tool needs to check the values for
    #    <link> before an RFC is published.  In draft production mode, the
    #    prep tool might remove some <link> elements during the draft
    #    submission process.
    # 
    #    This element appears as a child element of <rfc> (Section 2.45).
    # 
    #    Content model: this element does not have any contents.
    # 
    # 2.30.1.  "href" Attribute (Mandatory)
    # 
    #    The URI of the external document.
    # 
    # 2.30.2.  "rel" Attribute
    # 
    #    The relationship of the external document to this one.  The
    #    relationships are taken from the "Link Relations" registry maintained
    #    by IANA [LINKRELATIONS].
    # 
    # 2.31.  <middle>
    # 
    #    Represents the main content of the document.
    # 
    #    This element appears as a child element of <rfc> (Section 2.45).
    # 
    #    Content model:
    # 
    #    One or more <section> elements (Section 2.46)
    # 
    # 2.32.  <name>
    # 
    #    The name of the section, note, figure, or texttable.  This name can
    #    indicate markup of flowing text (for example, including references or
    #    making some characters use a fixed-width font).
    # 
    #    This element appears as a child element of <figure> (Section 2.25),
    #    <note> (Section 2.33), <references> (Section 2.42), <section>
    #    (Section 2.46), <table> (Section 2.54), and <texttable>
    #    (Section 3.8).
    # 
    #    Content model:
    # 
    #    In any order:
    # 
    #    o  Text
    # 
    #    o  <cref> elements (Section 2.16)
    # 
    #    o  <eref> elements (Section 2.24)
    # 
    #    o  <relref> elements (Section 2.44)
    # 
    #    o  <tt> elements (Section 2.62)
    # 
    #    o  <xref> elements (Section 2.66)
    # 
    # 2.33.  <note>
    # 
    #    Creates an unnumbered, titled block of text that appears after the
    #    Abstract.
    # 
    #    It is usually used for additional information to reviewers (Working
    #    Group information, mailing list, ...) or for additional publication
    #    information such as "IESG Notes".
    # 
    #    This element appears as a child element of <front> (Section 2.26).
    # 
    #    Content model:
    # 
    #    In this order:
    # 
    #    1.  One optional <name> element (Section 2.32)
    # 
    #    2.  In any order, but at least one of:
    # 
    #        *  <dl> elements (Section 2.20)
    # 
    #        *  <ol> elements (Section 2.34)
    # 
    #        *  <t> elements (Section 2.53)
    # 
    #        *  <ul> elements (Section 2.63)
    # 
    # 2.33.1.  "removeInRFC" Attribute
    # 
    #    If set to "true", this note is marked in the prep tool with text
    #    indicating that it should be removed before the document is published
    #    as an RFC.  That text will be "This note is to be removed before
    #    publishing as an RFC."
    # 
    #    Allowed values:
    # 
    #    o  "true"
    # 
    #    o  "false" (default)
    # 
    # 2.33.2.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 2.34.  <ol>
    # 
    #    An ordered list.  The labels on the items will be either a number or
    #    a letter, depending on the value of the style attribute.
    # 
    #    This element appears as a child element of <abstract> (Section 2.1),
    #    <aside> (Section 2.6), <blockquote> (Section 2.10), <dd>
    #    (Section 2.18), <li> (Section 2.29), <note> (Section 2.33), <section>
    #    (Section 2.46), <td> (Section 2.56), and <th> (Section 2.58).
    # 
    #    Content model:
    # 
    #    One or more <li> elements (Section 2.29)
    # 
    # 2.34.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the list.
    # 
    # 2.34.2.  "group" Attribute
    # 
    #    When the prep tool sees an <ol> element with a "group" attribute that
    #    has already been seen, it continues the numbering of the list from
    #    where the previous list with the same group name left off.  If an
    #    <ol> element has both a "group" attribute and a "start" attribute,
    #    the group's numbering is reset to the given start value.
    # 
    # 2.34.3.  "spacing" Attribute
    # 
    #    Defines whether or not there is a blank line between entries.
    #    spacing="normal" indicates a single blank line, while
    #    spacing="compact" indicates no space between.
    # 
    #    Allowed values:
    # 
    #    o  "normal" (default)
    # 
    #    o  "compact"
    # 
    # 2.34.4.  "start" Attribute
    # 
    #    The ordinal value at which to start the list.  This defaults to "1"
    #    and must be an integer of 0 or greater.
    # 
    # 2.34.5.  "type" Attribute
    # 
    #    The type of the labels on list items.  If the length of the type
    #    value is 1, the meaning is the same as it is for HTML:
    # 
    #    a  Lowercase letters (a, b, c, ...)
    # 
    #    A  Uppercase letters (A, B, C, ...)
    # 
    #    1  Decimal numbers (1, 2, 3, ...)
    # 
    #    i  Lowercase Roman numerals (i, ii, iii, ...)
    # 
    #    I  Uppercase Roman numerals (I, II, III, ...)
    # 
    #    For types "a" and "A", after the 26th entry, the numbering starts at
    #    "aa"/"AA", then "ab"/"AB", and so on.
    # 
    #    If the length of the type value is greater than 1, the value must
    #    contain a percent-encoded indicator and other text.  The value is a
    #    free-form text that allows counter values to be inserted using a
    #    "percent-letter" format.  For instance, "[REQ%d]" generates labels of
    #    the form "[REQ1]", where "%d" inserts the item number as a decimal
    #    number.
    # 
    #    The following formats are supported:
    # 
    #    %c Lowercase letters (a, b, c, ...)
    # 
    #    %C Uppercase letters (A, B, C, ...)
    # 
    #    %d Decimal numbers (1, 2, 3, ...)
    # 
    #    %i Lowercase Roman numerals (i, ii, iii, ...)
    # 
    #    %I Uppercase Roman numerals (I, II, III, ...)
    # 
    #    %% Represents a percent sign
    # 
    #    Other formats are reserved for future use.  Only one percent encoding
    #    other than "%%" is allowed in a type string.
    # 
    #    It is an error for the type string to be empty.  For bulleted lists,
    #    use the <ul> element.  For lists that have neither bullets nor
    #    numbers, use the <ul> element with the 'empty="true"' attribute.
    # 
    #    If no type attribute is given, the default type is the same as
    #    "type='%d.'".
    # 
    # 2.35.  <organization>
    # 
    #    Specifies the affiliation [RFC7322] of an author.
    # 
    #    This information appears both in the "Author's Address" section and
    #    on the front page (see [RFC7322] for more information).  If the value
    #    is long, an abbreviated variant can be specified in the "abbrev"
    #    attribute.
    # 
    #    This element appears as a child element of <author> (Section 2.7).
    # 
    #    Content model: only text content.
    # 
    # 2.35.1.  "abbrev" Attribute
    # 
    #    Abbreviated variant.
    # 
    # 2.35.2.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the organization's name.
    # 
    # 2.36.  <phone>
    # 
    #    Represents a phone number.
    # 
    #    The value is expected to be the scheme-specific part of a "tel" URI
    #    (and so does not include the prefix "tel:"), using the
    #    "global-number-digits" syntax.  See Section 3 of [RFC3966] for
    #    details.
    # 
    #    This element appears as a child element of <address> (Section 2.2).
    # 
    #    Content model: only text content.
    # 
    # 2.37.  <postal>
    # 
    #    Contains optional child elements providing postal information.  These
    #    elements will be displayed in an order that is specific to
    #    formatters.  A postal address can contain only a set of <street>,
    #    <city>, <region>, <code>, and <country> elements, or only an ordered
    #    set of <postalLine> elements, but not both.
    # 
    #    This element appears as a child element of <address> (Section 2.2).
    # 
    #    Content model:
    # 
    #    Either:
    # 
    #       In any order:
    # 
    #       *  <city> elements (Section 2.13)
    # 
    #       *  <code> elements (Section 2.14)
    # 
    #       *  <country> elements (Section 2.15)
    # 
    #       *  <region> elements (Section 2.43)
    # 
    #       *  <street> elements (Section 2.49)
    # 
    #    Or:
    # 
    #       One or more <postalLine> elements (Section 2.38)
    # 
    # 2.38.  <postalLine>
    # 
    #    Represents one line of a postal address.  When more than one
    #    <postalLine> is given, the prep tool emits them in the order given.
    # 
    #    This element appears as a child element of <postal> (Section 2.37).
    # 
    #    Content model: only text content.
    # 
    # 2.38.1.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the text in the address line.
    # 
    # 2.39.  <refcontent>
    # 
    #    Text that should appear between the title and the date of a
    #    reference.  The purpose of this element is to prevent the need to
    #    abuse <seriesInfo> to get such text in a reference.
    # 
    #    For example:
    # 
    #    <reference anchor="April1">
    #      <front>
    #        <title>On Being A Fool</title>
    #        <author initials="K." surname="Phunny" fullname="Knot Phunny"/>
    #        <date year="2000" month="April"/>
    #      </front>
    #      <refcontent>Self-published pamphlet</refcontent>
    #    </reference>
    # 
    #    would render as:
    # 
    #       [April1]     Phunny, K., "On Being A Fool", Self-published
    #                    pamphlet, April 2000.
    # 
    #    This element appears as a child element of <reference>
    #    (Section 2.40).
    # 
    #    Content model:
    # 
    #    In any order:
    # 
    #    o  Text
    # 
    #    o  <bcp14> elements (Section 2.9)
    # 
    #    o  <em> elements (Section 2.22)
    # 
    #    o  <strong> elements (Section 2.50)
    # 
    #    o  <sub> elements (Section 2.51)
    # 
    #    o  <sup> elements (Section 2.52)
    # 
    #    o  <tt> elements (Section 2.62)
    # 
    # 2.40.  <reference>
    # 
    #    Represents a bibliographic reference.
    # 
    #    This element appears as a child element of <referencegroup>
    #    (Section 2.41) and <references> (Section 2.42).
    # 
    #    Content model:
    # 
    #    In this order:
    # 
    #    1.  One <front> element (Section 2.26)
    # 
    #    2.  In any order:
    # 
    #        *  <annotation> elements (Section 2.3)
    # 
    #        *  <format> elements (Section 3.3)
    # 
    #        *  <refcontent> elements (Section 2.39)
    # 
    #        *  <seriesInfo> elements (Section 2.47; deprecated in this
    #           context)
    # 
    # 2.40.1.  "anchor" Attribute (Mandatory)
    # 
    #    Document-wide unique identifier for this reference.  Usually, this
    #    will be used both to "label" the reference in the "References"
    #    section and as an identifier in links to this reference entry.
    # 
    # 2.40.2.  "quoteTitle" Attribute
    # 
    #    Specifies whether or not the title in the reference should be quoted.
    #    This can be used to prevent quoting, such as on errata.
    # 
    #    Allowed values:
    # 
    #    o  "true" (default)
    # 
    #    o  "false"
    # 
    # 2.40.3.  "target" Attribute
    # 
    #    Holds the URI for the reference.
    # 
    # 2.41.  <referencegroup>
    # 
    #    Represents a list of bibliographic references that will be
    #    represented as a single reference.  This is most often used to
    #    reference STDs and BCPs, where a single reference (such as "BCP 9")
    #    may encompass more than one RFC.
    # 
    #    This element appears as a child element of <references>
    #    (Section 2.42).
    # 
    #    Content model:
    # 
    #    One or more <reference> elements (Section 2.40)
    # 
    # 2.41.1.  "anchor" Attribute (Mandatory)
    # 
    #    Document-wide unique identifier for this reference group.  Usually,
    #    this will be used both to "label" the reference group in the
    #    "References" section and as an identifier in links to this reference
    #    entry.
    # 
    # 2.42.  <references>
    # 
    #    Contains a set of bibliographic references.
    # 
    #    In the early days of the RFC Series, there was only one "References"
    #    section per RFC.  This convention was later changed to group
    #    references into two sets, "Normative" and "Informative", as described
    #    in [RFC7322].  This vocabulary supports the split with the <name>
    #    child element.  In general, the title should be either "Normative
    #    References" or "Informative References".
    # 
    #    This element appears as a child element of <back> (Section 2.8).
    # 
    #    Content model:
    # 
    #    In this order:
    # 
    #    1.  One optional <name> element (Section 2.32)
    # 
    #    2.  In any order:
    # 
    #        *  <reference> elements (Section 2.40)
    # 
    #        *  <referencegroup> elements (Section 2.41)
    # 
    # 2.42.1.  "anchor" Attribute
    # 
    #    An optional user-supplied identifier for this set of references.
    # 
    # 2.42.2.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 2.43.  <region>
    # 
    #    Provides the region name in a postal address.
    # 
    #    This element appears as a child element of <postal> (Section 2.37).
    # 
    #    Content model: only text content.
    # 
    # 2.43.1.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the region name.
    # 
    # 2.44.  <relref>
    # 
    #    Represents a link to a specific part of a document that appears in a
    #    <reference> element.  Formatters that have links (such as HTML and
    #    PDF) render <relref> elements as external hyperlinks to the specified
    #    part of the reference, creating the link target by combining the base
    #    URI from the <reference> element with the "relative" attribute from
    #    this element.  The "target" attribute is required, and it must be the
    #    anchor of a <reference> element.
    # 
    #    The "section" attribute is required, and the "relative" attribute is
    #    optional.  If the reference is not an RFC or Internet-Draft that is
    #    in the v3 format, the element needs to have a "relative" attribute;
    #    in this case, the value of the "section" attribute is ignored.
    # 
    #    An example of the <relref> element with text content might be:
    # 
    #          See
    #          <relref section="2.3" target="RFC9999" displayFormat="bare">
    #          the protocol overview</relref>
    #          for more information.
    # 
    #    An HTML formatter might generate:
    # 
    #          See
    #          <a href="http://www.rfc-editor.org/rfc/rfc9999.html#s-2.3">
    #          the protocol overview</a>
    #          for more information.
    # 
    #    Note that the URL in the above example might be different when the
    #    RFC Editor deploys the v3 format.
    # 
    #    This element appears as a child element of <annotation>
    #    (Section 2.3), <blockquote> (Section 2.10), <cref> (Section 2.16),
    #    <dd> (Section 2.18), <dt> (Section 2.21), <em> (Section 2.22), <li>
    #    (Section 2.29), <name> (Section 2.32), <preamble> (Section 3.6),
    #    <strong> (Section 2.50), <sub> (Section 2.51), <sup> (Section 2.52),
    #    <t> (Section 2.53), <td> (Section 2.56), <th> (Section 2.58), and
    #    <tt> (Section 2.62).
    # 
    #    Content model: only text content.
    # 
    # 2.44.1.  "displayFormat" Attribute
    # 
    #    This attribute is used to signal formatters what the desired format
    #    of the relative reference should be.  Formatters for document types
    #    that have linking capability should wrap each part of the displayed
    #    text in hyperlinks.  If there is content in the <relref> element,
    #    formatters will ignore the value of this attribute.
    # 
    #    "of"
    # 
    #       A formatter should display the relative reference as the word
    #       "Section" followed by a space, the contents of the "section"
    #       attribute followed by a space, the word "of", another space, and
    #       the value from the "target" attribute enclosed in square brackets.
    # 
    #       For example, with an input of:
    # 
    #          See
    #          <relref section="2.3" target="RFC9999" displayFormat="of"/>
    #          for an overview.
    # 
    #       An HTML formatter might generate:
    # 
    #          See
    #          <a href="http://www.rfc-editor.org/info/rfc9999#s-2.3">
    #          Section 2.3</a> of
    #          [<a href="#RFC9999">RFC9999</a>]
    #          for an overview.
    # 
    #       Note that "displayFormat='of'" is the default for <relref>, so it
    #       does not need to be given in a <relref> element if that format is
    #       desired.
    # 
    #    "comma"
    # 
    #       A formatter should display the relative reference as the value
    #       from the "target" attribute enclosed in square brackets, a comma,
    #       a space, the word "Section" followed by a space, and the "section"
    #       attribute.
    # 
    #       For example, with an input of:
    # 
    #          See
    #          <relref section="2.3" target="RFC9999" displayFormat="comma"/>,
    #          for an overview.
    # 
    #       An HTML formatter might generate:
    # 
    #          See
    #          [<a href="#RFC9999">RFC9999</a>],
    #          <a href="http://www.rfc-editor.org/info/rfc9999#s-2.3">
    #          Section 2.3</a>, for an overview.
    # 
    #    "parens"
    # 
    #       A formatter should display the relative reference as the value
    #       from the "target" attribute enclosed in square brackets, a space,
    #       a left parenthesis, the word "Section" followed by a space, the
    #       "section" attribute, and a right parenthesis.
    # 
    #       For example, with an input of:
    # 
    #          See
    #          <relref section="2.3" target="RFC9999" displayFormat="parens"/>
    #          for an overview.
    # 
    #       An HTML formatter might generate:
    # 
    #          See
    #          [<a href="#RFC9999">RFC9999</a>]
    #          (<a href="http://www.rfc-editor.org/info/rfc9999#s-2.3">
    #          Section 2.3</a>)
    #          for an overview.
    # 
    #    "bare"
    # 
    #       A formatter should display the relative reference as the contents
    #       of the "section" attribute and nothing else.  This is useful when
    #       there are multiple relative references to a single base reference.
    # 
    #       For example:
    # 
    #          See Sections
    #          <relref section="2.3" target="RFC9999" displayFormat="bare"/>
    #          and
    #          <relref section="2.4" target="RFC9999" displayFormat="of"/>
    #          for an overview.
    # 
    #       An HTML formatter might generate:
    # 
    #          See Sections
    #          <a href="http://www.rfc-editor.org/info/rfc9999#s-2.3">
    #          2.3</a>
    #          and
    #          <a href="http://www.rfc-editor.org/info/rfc9999#s-2.4">
    #          Section 2.4</a> of
    #          [<a href="#RFC9999">RFC9999</a>]
    #          for an overview.
    # 
    #    Allowed values:
    # 
    #    o  "of" (default)
    # 
    #    o  "comma"
    # 
    #    o  "parens"
    # 
    #    o  "bare"
    # 
    # 2.44.2.  "relative" Attribute
    # 
    #    Specifies a relative reference from the URI in the target reference.
    #    This value must include whatever leading character is needed to
    #    create the relative reference; typically, this is "#" for HTML
    #    documents.
    # 
    # 2.44.3.  "section" Attribute (Mandatory)
    # 
    #    Specifies a section of the target reference.  If the reference is not
    #    an RFC or Internet-Draft in the v3 format, it is an error.
    # 
    # 2.44.4.  "target" Attribute (Mandatory)
    # 
    #    The anchor of the reference for this element.  If this value is not
    #    an anchor to a <reference> or <referencegroup> element, it is an
    #    error.  If the reference at the target has no URI, it is an error.
    # 
    # 2.45.  <rfc>
    # 
    #    This is the root element of the xml2rfc vocabulary.
    # 
    #    Content model:
    # 
    #    In this order:
    # 
    #    1.  Optional <link> elements (Section 2.30)
    # 
    #    2.  One <front> element (Section 2.26)
    # 
    #    3.  One <middle> element (Section 2.31)
    # 
    #    4.  One optional <back> element (Section 2.8)
    # 
    # 2.45.1.  "category" Attribute
    # 
    #    Deprecated; instead, use the "name" attribute in <seriesInfo>.
    # 
    # 2.45.2.  "consensus" Attribute
    # 
    #    Affects the generated boilerplate.  Note that the values of "no" and
    #    "yes" are deprecated and are replaced by "false" (the default) and
    #    "true".
    # 
    #    See [RFC7841] for more information.
    # 
    #    Allowed values:
    # 
    #    o  "no"
    # 
    #    o  "yes"
    # 
    #    o  "false" (default)
    # 
    #    o  "true"
    # 
    # 2.45.3.  "docName" Attribute
    # 
    #    Deprecated; instead, use the "value" attribute in <seriesInfo>.
    # 
    # 2.45.4.  "indexInclude" Attribute
    # 
    #    Specifies whether or not a formatter is requested to include an index
    #    in generated files.  If the source file has no <iref> elements, an
    #    index is never generated.  This option is useful for generating
    #    documents where the source document has <iref> elements but the
    #    author no longer wants an index.
    # 
    #    Allowed values:
    # 
    #    o  "true" (default)
    # 
    #    o  "false"
    # 
    # 2.45.5.  "ipr" Attribute
    # 
    #    Represents the Intellectual Property status of the document.  See
    #    Appendix A.1 for details.
    # 
    # 2.45.6.  "iprExtract" Attribute
    # 
    #    Identifies a single section within the document for which extraction
    #    "as is" is explicitly allowed (only relevant for historic values of
    #    the "ipr" attribute).
    # 
    # 2.45.7.  "number" Attribute
    # 
    #    Deprecated; instead, use the "value" attribute in <seriesInfo>.
    # 
    # 2.45.8.  "obsoletes" Attribute
    # 
    #    A comma-separated list of RFC numbers or Internet-Draft names.
    # 
    #    The prep tool will parse the attribute value so that incorrect
    #    references can be detected.
    # 
    # 2.45.9.  "prepTime" Attribute
    # 
    #    The date that the XML was processed by a prep tool.  This is included
    #    in the XML file just before it is saved to disk.  The value is
    #    formatted using the "date-time" format defined in Section 5.6 of
    #    [RFC3339].  The "time-offset" should be "Z".
    # 
    # 2.45.10.  "seriesNo" Attribute
    # 
    #    Deprecated; instead, use the "value" attribute in <seriesInfo>.
    # 
    # 2.45.11.  "sortRefs" Attribute
    # 
    #    Specifies whether or not the prep tool will sort the references in
    #    each reference section.
    # 
    #    Allowed values:
    # 
    #    o  "true"
    # 
    #    o  "false" (default)
    # 
    # 2.45.12.  "submissionType" Attribute
    # 
    #    The document stream, as described in [RFC7841].  (The RFC Series
    #    Editor may change the list of allowed values in the future.)
    # 
    #    Allowed values:
    # 
    #    o  "IETF" (default)
    # 
    #    o  "IAB"
    # 
    #    o  "IRTF"
    # 
    #    o  "independent"
    # 
    # 2.45.13.  "symRefs" Attribute
    # 
    #    Specifies whether or not a formatter is requested to use symbolic
    #    references (such as "[RFC2119]").  If the value for this is "false",
    #    the references come out as numbers (such as "[3]").
    # 
    #    Allowed values:
    # 
    #    o  "true" (default)
    # 
    #    o  "false"
    # 
    # 2.45.14.  "tocDepth" Attribute
    # 
    #    Specifies the number of levels of headings that a formatter is
    #    requested to include in the table of contents; the default is "3".
    # 
    # 2.45.15.  "tocInclude" Attribute
    # 
    #    Specifies whether or not a formatter is requested to include a table
    #    of contents in generated files.
    # 
    #    Allowed values:
    # 
    #    o  "true" (default)
    # 
    #    o  "false"
    # 
    # 2.45.16.  "updates" Attribute
    # 
    #    A comma-separated list of RFC numbers or Internet-Draft names.
    # 
    #    The prep tool will parse the attribute value so that incorrect
    #    references can be detected.
    # 
    # 2.45.17.  "version" Attribute
    # 
    #    Specifies the version of xml2rfc syntax used in this document.  The
    #    only expected value (for now) is "3".
    # 
    # 2.46.  <section>
    # 
    #    Represents a section (when inside a <middle> element) or an appendix
    #    (when inside a <back> element).
    # 
    #    Subsections are created by nesting <section> elements inside
    #    <section> elements.  Sections are allowed to be empty.
    # 
    #    This element appears as a child element of <back> (Section 2.8),
    #    <boilerplate> (Section 2.11), <middle> (Section 2.31), and <section>
    #    (Section 2.46).
    # 
    #    Content model:
    # 
    #    In this order:
    # 
    #    1.  One optional <name> element (Section 2.32)
    # 
    #    2.  In any order:
    # 
    #        *  <artwork> elements (Section 2.5)
    # 
    #        *  <aside> elements (Section 2.6)
    # 
    #        *  <blockquote> elements (Section 2.10)
    # 
    #        *  <dl> elements (Section 2.20)
    # 
    #        *  <figure> elements (Section 2.25)
    # 
    #        *  <iref> elements (Section 2.27)
    # 
    #        *  <ol> elements (Section 2.34)
    # 
    #        *  <sourcecode> elements (Section 2.48)
    # 
    #        *  <t> elements (Section 2.53)
    # 
    #        *  <table> elements (Section 2.54)
    # 
    #        *  <texttable> elements (Section 3.8)
    # 
    #        *  <ul> elements (Section 2.63)
    # 
    #    3.  Optional <section> elements (Section 2.46)
    # 
    # 2.46.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this section.
    # 
    # 2.46.2.  "numbered" Attribute
    # 
    #    If set to "false", the formatter is requested to not display a
    #    section number.  The prep tool will verify that such a section is not
    #    followed by a numbered section in this part of the document and will
    #    verify that the section is a top-level section.
    # 
    #    Allowed values:
    # 
    #    o  "true" (default)
    # 
    #    o  "false"
    # 
    # 2.46.3.  "removeInRFC" Attribute
    # 
    #    If set to "true", this note is marked in the prep tool with text
    #    indicating that it should be removed before the document is published
    #    as an RFC.  That text will be "This note is to be removed before
    #    publishing as an RFC."
    # 
    #    Allowed values:
    # 
    #    o  "true"
    # 
    #    o  "false" (default)
    # 
    # 2.46.4.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 2.46.5.  "toc" Attribute
    # 
    #    Indicates to a formatter whether or not the section is to be included
    #    in a table of contents, if such a table of contents is produced.
    #    This only takes effect if the level of the section would have
    #    appeared in the table of contents based on the "tocDepth" attribute
    #    of the <rfc> element, and of course only if the table of contents is
    #    being created based on the "tocInclude" attribute of the <rfc>
    #    element.  If this is set to "exclude", any section below this one
    #    will be excluded as well.  The "default" value indicates inclusion of
    #    the section if it would be included by the tocDepth attribute of the
    #    <rfc> element.
    # 
    #    Allowed values:
    # 
    #    o  "include"
    # 
    #    o  "exclude"
    # 
    #    o  "default" (default)
    # 
    # 2.47.  <seriesInfo>
    # 
    #    Specifies the document series in which this document appears, and
    #    also specifies an identifier within that series.
    # 
    #    A processing tool determines whether it is working on an RFC or an
    #    Internet-Draft by inspecting the "name" attribute of a <seriesInfo>
    #    element inside the <front> element inside the <rfc> element, looking
    #    for "RFC" or "Internet-Draft".  (Specifying neither value in any of
    #    the <seriesInfo> elements can be useful for producing other types of
    #    documents but is out of scope for this specification.)
    # 
    #    It is invalid to have multiple <seriesInfo> elements inside the same
    #    <front> element containing the same "name" value.  Some combinations
    #    of <seriesInfo> "name" attribute values make no sense, such as having
    #    both <seriesInfo name="rfc"/> and <seriesInfo name="Internet-Draft"/>
    #    in the same <front> element.
    # 
    #    This element appears as a child element of <front> (Section 2.26) and
    #    <reference> (Section 2.40; deprecated in this context).
    # 
    #    Content model: this element does not have any contents.
    # 
    # 2.47.1.  "asciiName" Attribute
    # 
    #    The ASCII equivalent of the name field.
    # 
    # 2.47.2.  "asciiValue" Attribute
    # 
    #    The ASCII equivalent of the value field.
    # 
    # 2.47.3.  "name" Attribute (Mandatory)
    # 
    #    The name of the series.  The currently known values are "RFC",
    #    "Internet-Draft", and "DOI".  The RFC Series Editor may change this
    #    list in the future.
    # 
    #    Some of the values for "name" interact as follows:
    # 
    #    o  If a <front> element contains a <seriesInfo> element with a name
    #       of "Internet-Draft", it can also have at most one additional
    #       <seriesInfo> element with a "status" attribute whose value is of
    #       "standard", "full-standard", "bcp", "fyi", "informational",
    #       "experimental", or "historic" to indicate the intended status of
    #       this Internet-Draft, if it were to be later published as an RFC.
    #       If such an additional <seriesInfo> element has one of those
    #       statuses, the name needs to be "".
    # 
    #    o  If a <front> element contains a <seriesInfo> element with a name
    #       of "RFC", it can also have at most one additional <seriesInfo>
    #       element with a "status" attribute whose value is of
    #       "full-standard", "bcp", or "fyi" to indicate the current status of
    #       this RFC.  If such an additional <seriesInfo> element has one of
    #       those statuses, the "value" attribute for that name needs to be
    #       the number within that series.  That <front> element might also
    #       contain an additional <seriesInfo> element with the status of
    #       "info", "exp", or "historic" and a name of "" to indicate the
    #       status of the RFC.
    # 
    #    o  A <front> element that has a <seriesInfo> element that has the
    #       name "Internet-Draft" cannot also have a <seriesInfo> element that
    #       has the name "RFC".
    # 
    #    o  The <seriesInfo> element can contain the DOI for the referenced
    #       document.  This cannot be used when the <seriesInfo> element is an
    #       eventual child element of an <rfc> element -- only as an eventual
    #       child of a <reference> element.  The "value" attribute should use
    #       the form specified in [RFC7669].
    # 
    # 2.47.4.  "status" Attribute
    # 
    #    The status of this document.  The currently known values are
    #    "standard", "informational", "experimental", "bcp", "fyi", and
    #    "full-standard".  The RFC Series Editor may change this list in the
    #    future.
    # 
    # 2.47.5.  "stream" Attribute
    # 
    #    The stream (as described in [RFC7841]) that originated the document.
    #    (The RFC Series Editor may change this list in the future.)
    # 
    #    Allowed values:
    # 
    #    o  "IETF" (default)
    # 
    #    o  "IAB"
    # 
    #    o  "IRTF"
    # 
    #    o  "independent"
    # 
    # 2.47.6.  "value" Attribute (Mandatory)
    # 
    #    The identifier within the series specified by the "name" attribute.
    # 
    #    For BCPs, FYIs, RFCs, and STDs, this is the number within the series.
    #    For Internet-Drafts, it is the full draft name (ending with the
    #    two-digit version number).  For DOIs, the value is given, such as
    #    "10.17487/rfc1149", as described in [RFC7669].
    # 
    #    The name in the value should be the document name without any file
    #    extension.  For Internet-Drafts, the value for this attribute should
    #    be "draft-ietf-somewg-someprotocol-07", not
    #    "draft-ietf-somewg-someprotocol-07.txt".
    # 
    # 2.48.  <sourcecode>
    # 
    #    This element allows the inclusion of source code into the document.
    # 
    #    When rendered, source code is always shown in a monospace font.  When
    #    <sourcecode> is a child of <figure> or <section>, it provides full
    #    control of horizontal whitespace and line breaks.  When formatted, it
    #    is indented relative to the left margin of the enclosing element.  It
    #    is thus useful for source code and formal languages (such as ABNF
    #    [RFC5234] or the RNC notation used in this document).  (When
    #    <sourcecode> is a child of other elements, it flows with the text
    #    that surrounds it.)  Tab characters (U+0009) inside of this element
    #    are prohibited.
    # 
    #    For artwork such as character-based art, diagrams of message layouts,
    #    and so on, use the <artwork> element instead.
    # 
    #    Output formatters that do pagination should attempt to keep source
    #    code on a single page.  This is to prevent source code that is split
    #    across pages from looking like two separate pieces of code.
    # 
    #    See Section 5 for a description of how to deal with issues of using
    #    "&" and "<" characters in source code.
    # 
    #    This element appears as a child element of <blockquote>
    #    (Section 2.10), <dd> (Section 2.18), <figure> (Section 2.25), <li>
    #    (Section 2.29), <section> (Section 2.46), <td> (Section 2.56), and
    #    <th> (Section 2.58).
    # 
    #    Content model: only text content.
    # 
    # 2.48.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this source code.
    # 
    # 2.48.2.  "name" Attribute
    # 
    #    A filename suitable for the contents (such as for extraction to a
    #    local file).  This attribute can be helpful for other kinds of tools
    #    (such as automated syntax checkers, which work by extracting the
    #    source code).  Note that the "name" attribute does not need to be
    #    unique for <artwork> elements in a document.  If multiple
    #    <sourcecode> elements have the same "name" attribute, a formatter
    #    might assume that the elements are all fragments of a single file,
    #    and such a formatter can collect those fragments for later
    #    processing.
    # 
    # 2.48.3.  "src" Attribute
    # 
    #    The URI reference of a source file [RFC3986].
    # 
    #    It is an error to have both a "src" attribute and content in the
    #    <sourcecode> element.
    # 
    # 2.48.4.  "type" Attribute
    # 
    #    Specifies the type of the source code.  The value of this attribute
    #    is free text with certain values designated as preferred.
    # 
    #    The preferred values for <sourcecode> types are:
    # 
    #    o  abnf
    # 
    #    o  asn.1
    # 
    #    o  bash
    # 
    #    o  c++
    # 
    #    o  c
    # 
    #    o  cbor
    # 
    #    o  dtd
    # 
    #    o  java
    # 
    #    o  javascript
    # 
    #    o  json
    # 
    #    o  mib
    # 
    #    o  perl
    # 
    #    o  pseudocode
    # 
    #    o  python
    # 
    #    o  rnc
    # 
    #    o  xml
    # 
    #    o  yang
    # 
    #    The RFC Series Editor will maintain a complete list of the preferred
    #    values on the RFC Editor web site, and that list is expected to be
    #    updated over time.  Thus, a consumer of v3 XML should not cause a
    #    failure when it encounters an unexpected type or no type is
    #    specified.
    # 
    # 2.49.  <street>
    # 
    #    Provides a street address.
    # 
    #    This element appears as a child element of <postal> (Section 2.37).
    # 
    #    Content model: only text content.
    # 
    # 2.49.1.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the street address.
    # 
    # 2.50.  <strong>
    # 
    #    Indicates text that is semantically strong.  Text enclosed within
    #    this element will be displayed as bold after processing.  This
    #    element can be combined with other character formatting elements, and
    #    the formatting will be additive.
    def render_strong(self, e, **kwargs):
        # Render text with leading and trailing '_'
        text = '*%s*' % self.inside_text_renderer(e, **kwargs)
        text += e.tail
        return text


    # 2.51.  <sub>
    # 
    #    Causes the text to be displayed as subscript, approximately half a
    #    letter-height lower than normal text.  This element can be combined
    #    with other character formatting elements, and the formatting will be
    #    additive.
    def render_sub(self, e, **kwargs):
        # Render text with leading and trailing '_'
        text = '_(%s)' % self.inside_text_renderer(e, **kwargs)
        text += e.tail
        return text


    # 2.52.  <sup>
    # 
    #    Causes the text to be displayed as superscript, approximately half a
    #    letter-height higher than normal text.  This element can be combined
    #    with other character formatting elements, and the formatting will be
    #    additive.
    def render_sup(self, e, **kwargs):
        # Render text with leading and trailing '_'
        text = '^(%s)' % self.inside_text_renderer(e, **kwargs)
        text += e.tail
        return text


    # 2.53.  <t>
    # 
    #    Contains a paragraph of text.
    # 
    #    This element appears as a child element of <abstract> (Section 2.1),
    #    <aside> (Section 2.6), <blockquote> (Section 2.10), <dd>
    #    (Section 2.18), <li> (Section 2.29), <list> (Section 3.4), <note>
    #    (Section 2.33), <section> (Section 2.46), <td> (Section 2.56), and
    #    <th> (Section 2.58).
    # 
    #    Content model:
    # 
    #    In any order:
    # 
    #    o  Text
    # 
    #    o  <bcp14> elements (Section 2.9)
    # 
    #    o  <cref> elements (Section 2.16)
    # 
    #    o  <em> elements (Section 2.22)
    # 
    #    o  <eref> elements (Section 2.24)
    # 
    #    o  <iref> elements (Section 2.27)
    # 
    #    o  <list> elements (Section 3.4)
    # 
    #    o  <relref> elements (Section 2.44)
    # 
    #    o  <spanx> elements (Section 3.7)
    # 
    #    o  <strong> elements (Section 2.50)
    # 
    #    o  <sub> elements (Section 2.51)
    # 
    #    o  <sup> elements (Section 2.52)
    # 
    #    o  <tt> elements (Section 2.62)
    # 
    #    o  <vspace> elements (Section 3.10)
    # 
    #    o  <xref> elements (Section 2.66)
    # 
    # 2.53.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this paragraph.
    # 
    # 2.53.2.  "hangText" Attribute
    # 
    #    Deprecated.  Instead, use <dd> inside of a definition list (<dl>).
    # 
    # 2.53.3.  "keepWithNext" Attribute
    # 
    #    Acts as a hint to the output formatters that do pagination to do a
    #    best-effort attempt to keep the paragraph with the next element,
    #    whatever that happens to be.  For example, the HTML output @media
    #    print CSS ("CSS" refers to Cascading Style Sheets) might translate
    #    this to page-break-after: avoid.  For PDF, the paginator could
    #    attempt to keep the paragraph with the next element.  Note: this
    #    attribute is strictly a hint and not always actionable.
    # 
    #    Allowed values:
    # 
    #    o  "false" (default)
    # 
    #    o  "true"
    # 
    # 2.53.4.  "keepWithPrevious" Attribute
    # 
    #    Acts as a hint to the output formatters that do pagination to do a
    #    best-effort attempt to keep the paragraph with the previous element,
    #    whatever that happens to be.  For example, the HTML output @media
    #    print CSS might translate this to page-break-before: avoid.  For PDF,
    #    the paginator could attempt to keep the paragraph with the previous
    #    element.  Note: this attribute is strictly a hint and not always
    #    actionable.
    # 
    #    Allowed values:
    # 
    #    o  "false" (default)
    # 
    #    o  "true"
    # 
    # 2.54.  <table>
    # 
    #    Contains a table with a caption with the table number.  If the
    #    element contains a <name> element, the caption will also show that
    #    name.
    # 
    #    Inside the <table> element is, optionally, a <thead> element to
    #    contain the rows that will be the table's heading and, optionally, a
    #    <tfoot> element to contain the rows of the table's footer.  If the
    #    XML is converted to a representation that has page breaks (such as
    #    PDFs or printed HTML), the header and footer are meant to appear on
    #    each page.
    # 
    #    This element appears as a child element of <aside> (Section 2.6) and
    #    <section> (Section 2.46).
    # 
    #    Content model:
    # 
    #    In this order:
    # 
    #    1.  One optional <name> element (Section 2.32)
    # 
    #    2.  Optional <iref> elements (Section 2.27)
    # 
    #    3.  One optional <thead> element (Section 2.59)
    # 
    #    4.  One or more <tbody> elements (Section 2.55)
    # 
    #    5.  One optional <tfoot> element (Section 2.57)
    # 
    # 2.54.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for this table.
    # 
    # 2.55.  <tbody>
    # 
    #    A container for a set of body rows for a table.
    # 
    #    This element appears as a child element of <table> (Section 2.54).
    # 
    #    Content model:
    # 
    #    One or more <tr> elements (Section 2.61)
    # 
    # 2.55.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the tbody.
    # 
    # 2.56.  <td>
    # 
    #    A cell in a table row.
    # 
    #    This element appears as a child element of <tr> (Section 2.61).
    # 
    #    Content model:
    # 
    #    Either:
    # 
    #       In any order, but at least one of:
    # 
    #       *  <artwork> elements (Section 2.5)
    # 
    #       *  <dl> elements (Section 2.20)
    # 
    #       *  <figure> elements (Section 2.25)
    # 
    #       *  <ol> elements (Section 2.34)
    # 
    #       *  <sourcecode> elements (Section 2.48)
    # 
    #       *  <t> elements (Section 2.53)
    # 
    #       *  <ul> elements (Section 2.63)
    # 
    #    Or:
    # 
    #       In any order:
    # 
    #       *  Text
    # 
    #       *  <bcp14> elements (Section 2.9)
    # 
    #       *  <br> elements (Section 2.12)
    # 
    #       *  <cref> elements (Section 2.16)
    # 
    #       *  <em> elements (Section 2.22)
    # 
    #       *  <eref> elements (Section 2.24)
    # 
    #       *  <iref> elements (Section 2.27)
    # 
    #       *  <relref> elements (Section 2.44)
    # 
    #       *  <strong> elements (Section 2.50)
    # 
    #       *  <sub> elements (Section 2.51)
    # 
    #       *  <sup> elements (Section 2.52)
    # 
    #       *  <tt> elements (Section 2.62)
    # 
    #       *  <xref> elements (Section 2.66)
    # 
    # 2.56.1.  "align" Attribute
    # 
    #    Controls whether the content of the cell appears left justified
    #    (default), centered, or right justified.  Note that "center" or
    #    "right" will probably only work well in cells with plain text; any
    #    other elements might make the contents render badly.
    # 
    #    Allowed values:
    # 
    #    o  "left" (default)
    # 
    #    o  "center"
    # 
    #    o  "right"
    # 
    # 2.56.2.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the cell.
    # 
    # 2.56.3.  "colspan" Attribute
    # 
    #    The number of columns that the cell is to span.  For example, setting
    #    "colspan='3'" indicates that the cell occupies the same horizontal
    #    space as three cells of a row without any "colspan" attributes.
    # 
    # 2.56.4.  "rowspan" Attribute
    # 
    #    The number of rows that the cell is to span.  For example, setting
    #    "rowspan='3'" indicates that the cell occupies the same vertical
    #    space as three rows.
    # 
    # 2.57.  <tfoot>
    # 
    #    A container for a set of footer rows for a table.
    # 
    #    This element appears as a child element of <table> (Section 2.54).
    # 
    #    Content model:
    # 
    #    One or more <tr> elements (Section 2.61)
    # 
    # 2.57.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the tfoot.
    # 
    # 2.58.  <th>
    # 
    #    A cell in a table row.  When rendered, this will normally come out in
    #    boldface; other than that, there is no difference between this and
    #    the <td> element.
    # 
    #    This element appears as a child element of <tr> (Section 2.61).
    # 
    #    Content model:
    # 
    #    Either:
    # 
    #       In any order, but at least one of:
    # 
    #       *  <artwork> elements (Section 2.5)
    # 
    #       *  <dl> elements (Section 2.20)
    # 
    #       *  <figure> elements (Section 2.25)
    # 
    #       *  <ol> elements (Section 2.34)
    # 
    #       *  <sourcecode> elements (Section 2.48)
    # 
    #       *  <t> elements (Section 2.53)
    # 
    #       *  <ul> elements (Section 2.63)
    # 
    #    Or:
    # 
    #       In any order:
    # 
    #       *  Text
    # 
    #       *  <bcp14> elements (Section 2.9)
    # 
    #       *  <br> elements (Section 2.12)
    # 
    #       *  <cref> elements (Section 2.16)
    # 
    #       *  <em> elements (Section 2.22)
    # 
    #       *  <eref> elements (Section 2.24)
    # 
    #       *  <iref> elements (Section 2.27)
    # 
    #       *  <relref> elements (Section 2.44)
    # 
    #       *  <strong> elements (Section 2.50)
    # 
    #       *  <sub> elements (Section 2.51)
    # 
    #       *  <sup> elements (Section 2.52)
    # 
    #       *  <tt> elements (Section 2.62)
    # 
    #       *  <xref> elements (Section 2.66)
    # 
    # 2.58.1.  "align" Attribute
    # 
    #    Controls whether the content of the cell appears left justified
    #    (default), centered, or right justified.  Note that "center" or
    #    "right" will probably only work well in cells with plain text; any
    #    other elements might make the contents render badly.
    # 
    #    Allowed values:
    # 
    #    o  "left" (default)
    # 
    #    o  "center"
    # 
    #    o  "right"
    # 
    # 2.58.2.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the row.
    # 
    # 2.58.3.  "colspan" Attribute
    # 
    #    The number of columns that the cell is to span.  For example, setting
    #    "colspan='3'" indicates that the cell occupies the same horizontal
    #    space as three cells of a row without any "colspan" attributes.
    # 
    # 2.58.4.  "rowspan" Attribute
    # 
    #    The number of rows that the cell is to span.  For example, setting
    #    "rowspan='3'" indicates that the cell occupies the same vertical
    #    space as three rows.
    # 
    # 2.59.  <thead>
    # 
    #    A container for a set of header rows for a table.
    # 
    #    This element appears as a child element of <table> (Section 2.54).
    # 
    #    Content model:
    # 
    #    One or more <tr> elements (Section 2.61)
    # 
    # 2.59.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the thead.
    # 
    # 2.60.  <title>
    # 
    #    Represents the document title.
    # 
    #    When this element appears in the <front> element of the current
    #    document, the title might also appear in page headers or footers.  If
    #    it is long (~40 characters), the "abbrev" attribute can be used to
    #    specify an abbreviated variant.
    # 
    #    This element appears as a child element of <front> (Section 2.26).
    # 
    #    Content model: only text content.
    # 
    # 2.60.1.  "abbrev" Attribute
    # 
    #    Specifies an abbreviated variant of the document title.
    # 
    # 2.60.2.  "ascii" Attribute
    # 
    #    The ASCII equivalent of the title.
    # 
    # 2.61.  <tr>
    # 
    #    A row of a table.
    # 
    #    This element appears as a child element of <tbody> (Section 2.55),
    #    <tfoot> (Section 2.57), and <thead> (Section 2.59).
    # 
    #    Content model:
    # 
    #    In any order, but at least one of:
    # 
    #    o  <td> elements (Section 2.56)
    # 
    #    o  <th> elements (Section 2.58)
    # 
    # 2.61.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the row.
    # 
    # 2.62.  <tt>
    # 
    #    Causes the text to be displayed in a constant-width font.  This
    #    element can be combined with other character formatting elements, and
    #    the formatting will be additive.
    def render_tt(self, e, **kwargs):
        # Render text with leading and trailing '_'
        text = '<%s>' % self.inside_text_renderer(e, **kwargs)
        text += e.tail
        return text


    # 2.63.  <ul>
    # 
    #    An unordered list.  The labels on the items will be symbols picked by
    #    the formatter.
    # 
    #    This element appears as a child element of <abstract> (Section 2.1),
    #    <aside> (Section 2.6), <blockquote> (Section 2.10), <dd>
    #    (Section 2.18), <li> (Section 2.29), <note> (Section 2.33), <section>
    #    (Section 2.46), <td> (Section 2.56), and <th> (Section 2.58).
    # 
    #    Content model:
    # 
    #    One or more <li> elements (Section 2.29)
    # 
    # 2.63.1.  "anchor" Attribute
    # 
    #    Document-wide unique identifier for the list.
    # 
    # 2.63.2.  "empty" Attribute
    # 
    #    Defines whether or not the label is empty.  empty="true" indicates
    #    that no label will be shown.
    # 
    #    Allowed values:
    # 
    #    o  "false" (default)
    # 
    #    o  "true"
    # 
    # 2.63.3.  "spacing" Attribute
    # 
    #    Defines whether or not there is a blank line between entries.
    #    spacing="normal" indicates a single blank line, while
    #    spacing="compact" indicates no space between.
    # 
    #    Allowed values:
    # 
    #    o  "normal" (default)
    # 
    #    o  "compact"
    # 
    # 2.64.  <uri>
    # 
    #    Contains a web address associated with the author.
    # 
    #    The contents should be a valid URI; this most likely will be an
    #    "http:" or "https:" URI.
    # 
    #    This element appears as a child element of <address> (Section 2.2).
    # 
    #    Content model: only text content.
    # 
    # 2.65.  <workgroup>
    # 
    #    This element is used to specify the Working Group (IETF) or Research
    #    Group (IRTF) from which the document originates, if any.  The
    #    recommended format is the official name of the Working Group (with
    #    some capitalization).
    # 
    #    In Internet-Drafts, this is used in the upper left corner of the
    #    boilerplate, replacing the "Network Working Group" string.
    #    Formatting software can append the words "Working Group" or "Research
    #    Group", depending on the "submissionType" property of the <rfc>
    #    element (Section 2.45.12).
    # 
    #    This element appears as a child element of <front> (Section 2.26).
    # 
    #    Content model: only text content.
    # 
    # 2.66.  <xref>
    # 
    #    A reference to an anchor in this document.  Formatters that have
    #    links (such as HTML and PDF) are likely to render <xref> elements as
    #    internal hyperlinks.  This element is useful for referring to
    #    references in the "References" section, to specific sections of this
    #    document, to specific figures, and so on.  The "target" attribute is
    #    required.
    # 
    #    This element appears as a child element of <annotation>
    #    (Section 2.3), <blockquote> (Section 2.10), <c> (Section 3.1), <cref>
    #    (Section 2.16), <dd> (Section 2.18), <dt> (Section 2.21), <em>
    #    (Section 2.22), <li> (Section 2.29), <name> (Section 2.32),
    #    <postamble> (Section 3.5), <preamble> (Section 3.6), <strong>
    #    (Section 2.50), <sub> (Section 2.51), <sup> (Section 2.52), <t>
    #    (Section 2.53), <td> (Section 2.56), <th> (Section 2.58), <tt>
    #    (Section 2.62), and <ttcol> (Section 3.9).
    # 
    #    Content model: only text content.
    # 
    # 2.66.1.  "format" Attribute
    # 
    #    This attribute signals to formatters what the desired format of the
    #    reference should be.  Formatters for document types that have linking
    #    capability should wrap the displayed text in hyperlinks.
    # 
    #    "counter"
    # 
    #       The "derivedContent" attribute will contain just a counter.  This
    #       is used for targets that are <section>, <figure>, <table>, or
    #       items in an ordered list.  Using "format='counter'" where the
    #       target is any other type of element is an error.
    # 
    #       For example, with an input of:
    # 
    #          <section anchor="overview">Protocol Overview</section>
    #          . . .
    #          See Section <xref target="overview" format="counter"/>
    #          for an overview.
    # 
    #       An HTML formatter might generate:
    # 
    #          See Section <a href="#overview">1.7</a> for an overview.
    # 
    #    "default"
    # 
    #       If the element has no content, the "derivedContent" attribute will
    #       contain a text fragment that describes the referenced part
    #       completely, such as "XML" for a target that is a <reference>, or
    #       "Section 2" or "Table 4" for a target to a non-reference.  (If the
    #       element has content, the "derivedContent" attribute is filled with
    #       the content.)
    # 
    #       For example, with an input of:
    # 
    #          <section anchor="overview">Protocol Overview</section>
    #          . . .
    #          See <xref target="overview"/> for an overview.
    # 
    #       An HTML formatter might generate:
    # 
    #          See <a href="#overview">Section 1.7</a> for an overview.
    # 
    #    "none"
    # 
    #       Deprecated.
    # 
    #    "title"
    # 
    #       If the target is a <reference> element, the "derivedContent"
    #       attribute will contain the name of the reference, extracted from
    #       the <title> child of the <front> child of the reference.  Or, if
    #       the target element has a <name> child element, the
    #       "derivedContent" attribute will contain the text content of that
    #       <name> element concatenated with the text content of each
    #       descendant node of <name> (that is, stripping out all of the XML
    #       markup, leaving only the text).  Or, if the target element does
    #       not contain a <name> child element, the "derivedContent" attribute
    #       will contain the name of the "anchor" attribute of that element
    #       with no other adornment.
    # 
    #    Allowed values:
    # 
    #    o  "default" (default)
    # 
    #    o  "title"
    # 
    #    o  "counter"
    # 
    #    o  "none"
    # 
    # 2.66.2.  "pageno" Attribute
    # 
    #    Deprecated.
    # 
    #    Allowed values:
    # 
    #    o  "true"
    # 
    #    o  "false" (default)
    # 
    # 2.66.3.  "target" Attribute (Mandatory)
    # 
    #    Identifies the document component being referenced.  The value needs
    #    to match the value of the "anchor" attribute of an element in the
    #    document; otherwise, it is an error.
