# coding: utf-8

'''
Created on 3 may 2012

@author: Marc-Antoine Gouillart
@license: Apache v2
'''

_WINRS_URI="http://schemas.microsoft.com/wbem/wsman/1/windows/shell"
WINRS_CMD_URI="http://schemas.microsoft.com/wbem/wsman/1/windows/shell/cmd"
WINRS_CREATE_URI="http://schemas.xmlsoap.org/ws/2004/09/transfer/Create"
WINRS_COMMAND_URI="http://schemas.microsoft.com/wbem/wsman/1/windows/shell/Command"
WINRS_RECEIVE_URI="http://schemas.microsoft.com/wbem/wsman/1/windows/shell/Receive"
WINRS_DELETE_URI="http://schemas.xmlsoap.org/ws/2004/09/transfer/Delete"
WINRS_SEND_URI="http://schemas.microsoft.com/wbem/wsman/1/windows/shell/Send"

WINRS_CREATE_BODY_XML="<Shell xmlns='%s'><InputStreams>stdin</InputStreams><OutputStreams>stdout stderr</OutputStreams></Shell>" %_WINRS_URI
WINRS_COMMAND_OPTION_XML="<w:OptionSet><w:Option Name='WINRS_CONSOLEMODE_STDIN'>FALSE</w:Option><w:Option Name='WINRS_SKIP_CMD_SHELL'>TRUE</w:Option></w:OptionSet>"
WINRS_COMMAND_BODY_XML="<CommandLine xmlns='%s'><Command>{Command}</Command><Arguments>{Arguments}</Arguments></CommandLine>" %_WINRS_URI
WINRS_RECEIVE_BODY_XML="<Receive SequenceId='{SequenceId}' xmlns='%s'><DesiredStream CommandId='{CommandId}'>stdout stderr</DesiredStream></Receive>" %_WINRS_URI
WINRS_SEND_BODY_XML="<Send xmlns='%s'> <Stream Name='stdin' CommandId='{CommandId}'>{Base64Flow}</Stream></Send>" %_WINRS_URI

WINRS_SELECTORSET = "<w:SelectorSet><w:Selector Name='ShellId'>%s</w:Selector></w:SelectorSet>"

SOAP_ENVELOPE_XML="""
<s:Envelope xmlns:s='http://www.w3.org/2003/05/soap-envelope'
            xmlns:a='http://schemas.xmlsoap.org/ws/2004/08/addressing'
            xmlns:w='http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd'>
        <s:Header>
                <a:To>{Url}</a:To>
                <w:ResourceURI s:mustUnderstand='true'>{ResourceUri}</w:ResourceURI>
                <a:ReplyTo>
                        <a:Address s:mustUnderstand='true'>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</a:Address>
                </a:ReplyTo>
                <a:Action s:mustUnderstand='true'>{ActionUri}</a:Action>
                <w:MaxEnvelopeSize s:mustUnderstand='true'>153600</w:MaxEnvelopeSize>
                <a:MessageID>uuid:{MessageId}</a:MessageID>
                <w:Locale xml:lang='en-US' s:mustUnderstand='false'></w:Locale>
                <!--SelectorSet-->
                <!--OptionSet-->
                <w:OperationTimeout>PT60.000S</w:OperationTimeout>
        </s:Header>
        <s:Body><!--Body--></s:Body>
</s:Envelope>"""



